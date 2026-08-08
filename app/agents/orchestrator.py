"""
Real LangGraph multi-agent orchestration — matches Module 9 exactly.
Wires: NLP -> Symptom Classification -> RAG -> Knowledge Graph ->
Prompt Builder -> Guardrail check -> LLM.
"""
from typing import TypedDict, Optional
import base64
from langgraph.graph import StateGraph, END

from app.nlp.extractor import extract_symptoms, needs_followup
from app.ml.predict import predict_conditions
from app.rag.retriever import retrieve
from app.kg.neo4j_client import get_related_entities
from app.guardrails.safety import apply_guardrail
from app.prompt_builder import build_messages
from app.llm.openai_client import (
    generate_response, analyze_medical_image,
    LLMNotConfiguredError, LLMUnavailableError,
)
from app.memory.session_memory import get_recent_history_text
from app.ocr.ocr_pii import process_document_bytes


class WorkflowState(TypedDict, total=False):
    session_id: str
    query: str
    image_b64: Optional[str]          # set when the request includes an uploaded image
    ocr_text: Optional[str]            # redacted text extracted from an uploaded report/prescription
    ocr_error: Optional[str]           # OCR failures are non-fatal; image analysis can still continue
    vision_findings: Optional[str]     # structured findings text from the Vision LLM
    vision_error: Optional[str]        # set if vision call failed (non-fatal, degrades gracefully)
    guardrail_message: Optional[str]
    extraction: dict
    predicted_conditions: list
    rag_docs: list
    kg_data: dict
    conversation_history: str
    final_response: str
    error: Optional[str]


# ---- Nodes ----

def guardrail_node(state: WorkflowState) -> WorkflowState:
    message = apply_guardrail(state["query"])
    state["guardrail_message"] = message
    print(
        f"[pipeline][{state['session_id']}][guardrail] "
        f"{'Escalation triggered' if message else 'Passed'}"
    )
    return state


def vision_node(state: WorkflowState) -> WorkflowState:
    """
    Matches Module 6: the Vision LLM only produces structured findings —
    it does NOT answer the user directly. Those findings get merged into
    the query text so every downstream node (NLP, RAG, KG) treats them
    exactly like a text-described symptom, keeping the final answer
    grounded through the same RAG/KG/Guardrail pipeline rather than
    trusting the vision model's raw interpretation.
    """
    try:
        print(f"[pipeline][{state['session_id']}][vision] Starting image analysis")
        findings = analyze_medical_image(state["image_b64"], state["query"])
        state["vision_findings"] = findings
        # Merge findings into the query text itself so NLP extraction,
        # RAG retrieval, and the prompt all see the combined context.
        state["query"] = f"{state['query']}\n\n[Image findings: {findings}]"
        print(f"[pipeline][{state['session_id']}][vision] Findings merged into downstream query")
    except (LLMNotConfiguredError, LLMUnavailableError) as e:
        # Vision is best-effort: if it fails, continue with the original
        # text query alone rather than failing the whole request — matches
        # Module 6's documented fallback: "Continue with text-only
        # processing whenever possible." Deliberately NOT setting
        # state["error"] here, since that field means "the whole pipeline
        # failed" downstream in run_pipeline() — a failed vision call
        # should degrade, not abort.
        state["vision_findings"] = None
        state["vision_error"] = str(e)
        print(f"[pipeline][{state['session_id']}][vision] Unavailable; continuing text-only: {e}")
    return state


def ocr_node(state: WorkflowState) -> WorkflowState:
    """Extract and redact text before it is sent to RAG or an LLM.

    A non-empty OCR result identifies the upload as a document-like image.
    That path uses the redacted text for RAG cross-checking and skips Vision,
    so raw report content is not sent to the Vision model. A photo with no
    readable text continues to the Vision path instead.
    """
    try:
        print(f"[pipeline][{state['session_id']}][ocr] Starting Tesseract extraction")
        image_bytes = base64.b64decode(state["image_b64"], validate=True)
        redacted_text = process_document_bytes(image_bytes).strip()
        state["ocr_text"] = redacted_text
        if redacted_text:
            state["query"] = f"{state['query']}\n\n[OCR-extracted report text: {redacted_text}]"
        print(
            f"[pipeline][{state['session_id']}][ocr] Completed "
            f"(redacted_text_chars={len(redacted_text)})"
        )
    except Exception as e:
        state["ocr_text"] = None
        state["ocr_error"] = str(e)
        print(f"[pipeline][{state['session_id']}][ocr] Unavailable; continuing to Vision: {e}")
    return state


def nlp_node(state: WorkflowState) -> WorkflowState:
    state["extraction"] = extract_symptoms(state["query"])
    print(f"[pipeline][{state['session_id']}][nlp] Completed")
    return state


def classify_node(state: WorkflowState) -> WorkflowState:
    symptoms = state["extraction"]["symptoms"]
    if symptoms:
        state["predicted_conditions"] = predict_conditions(symptoms)
    else:
        state["predicted_conditions"] = []
        print(f"[pipeline][{state['session_id']}][classify] Skipped: no symptoms extracted")
    if symptoms:
        print(f"[pipeline][{state['session_id']}][classify] Completed")
    return state


def rag_node(state: WorkflowState) -> WorkflowState:
    state["rag_docs"] = retrieve(state["query"])
    print(f"[pipeline][{state['session_id']}][rag] Completed")
    return state


def kg_node(state: WorkflowState) -> WorkflowState:
    top_condition = None
    if state.get("predicted_conditions"):
        top_condition = state["predicted_conditions"][0]["condition"]

    if top_condition:
        state["kg_data"] = get_related_entities(top_condition)
        print(
            f"[pipeline][{state['session_id']}][kg] Completed "
            f"(condition={top_condition!r}, available={state['kg_data'].get('available', False)})"
        )
    else:
        state["kg_data"] = {"available": False, "medications": [], "specialists": [], "symptoms": []}
        print(f"[pipeline][{state['session_id']}][kg] Skipped: no predicted condition")
    return state


def memory_node(state: WorkflowState) -> WorkflowState:
    state["conversation_history"] = get_recent_history_text(state["session_id"])
    print(f"[pipeline][{state['session_id']}][memory] Completed")
    return state


def generate_node(state: WorkflowState) -> WorkflowState:
    messages = build_messages(
        query=state["query"],
        conversation_history=state["conversation_history"],
        rag_docs=state["rag_docs"],
        predicted_conditions=state["predicted_conditions"],
        kg_data=state["kg_data"],
    )
    print(
        f"[pipeline][{state['session_id']}][prompt] Built "
        f"(rag_docs={len(state['rag_docs'])}, predictions={len(state['predicted_conditions'])}, "
        f"kg_available={state['kg_data'].get('available', False)})"
    )
    try:
        state["final_response"] = generate_response(messages)
        print(f"[pipeline][{state['session_id']}][generate] Completed")
    except LLMNotConfiguredError as e:
        state["error"] = str(e)
        state["final_response"] = None
        print(f"[pipeline][{state['session_id']}][generate] Failed: {e}")
    except LLMUnavailableError as e:
        state["error"] = str(e)
        state["final_response"] = None
        print(f"[pipeline][{state['session_id']}][generate] Failed: {e}")
    return state


# ---- Routing ----

def route_after_guardrail(state: WorkflowState) -> str:
    if state.get("guardrail_message"):
        print(f"[pipeline][{state['session_id']}][route] guardrail -> END")
        return "escalate"
    # Matches Module 9's conditional routing: image requests take a
    # different path (through Vision first) than plain text requests —
    # only the required nodes execute for a given request.
    if state.get("image_b64"):
        print(f"[pipeline][{state['session_id']}][route] image request -> ocr")
        return "has_image"
    print(f"[pipeline][{state['session_id']}][route] text request -> nlp")
    return "text_only"


def route_after_ocr(state: WorkflowState) -> str:
    if state.get("ocr_text"):
        print(f"[pipeline][{state['session_id']}][route] OCR document text found -> nlp/rag")
        return "document_text"
    print(f"[pipeline][{state['session_id']}][route] no OCR text -> vision")
    return "image_analysis"


def build_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("guardrail_check", guardrail_node)
    graph.add_node("ocr", ocr_node)
    graph.add_node("vision", vision_node)
    graph.add_node("nlp", nlp_node)
    graph.add_node("classify", classify_node)
    graph.add_node("rag", rag_node)
    graph.add_node("kg", kg_node)
    graph.add_node("memory", memory_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("guardrail_check")

    graph.add_conditional_edges(
        "guardrail_check",
        route_after_guardrail,
        {"escalate": END, "has_image": "ocr", "text_only": "nlp"},
    )

    graph.add_conditional_edges(
        "ocr",
        route_after_ocr,
        {"document_text": "nlp", "image_analysis": "vision"},
    )
    graph.add_edge("vision", "nlp")  # vision findings get merged into query, then flow through NLP same as text
    graph.add_edge("nlp", "classify")
    graph.add_edge("classify", "rag")
    graph.add_edge("rag", "kg")
    graph.add_edge("kg", "memory")
    graph.add_edge("memory", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        print("[pipeline] Compiling LangGraph workflow")
        _compiled_graph = build_graph()
    return _compiled_graph


def run_pipeline(session_id: str, query: str, image_b64: str | None = None) -> dict:
    graph = get_graph()
    print(
        f"[pipeline][{session_id}] Started "
        f"(query_chars={len(query)}, has_image={bool(image_b64)})"
    )
    initial_state: WorkflowState = {"session_id": session_id, "query": query}
    if image_b64:
        initial_state["image_b64"] = image_b64
    result = graph.invoke(initial_state)

    if result.get("guardrail_message"):
        print(f"[pipeline][{session_id}] Finished: escalated")
        return {
            "response": result["guardrail_message"],
            "escalated": True,
            "sources": [],
        }

    if result.get("error"):
        print(f"[pipeline][{session_id}] Finished: error")
        return {
            "response": None,
            "error": result["error"],
            "escalated": False,
            "sources": [d["topic"] for d in result.get("rag_docs", [])],
        }

    print(f"[pipeline][{session_id}] Finished: response generated")
    return {
        "response": result["final_response"],
        "escalated": False,
        "predicted_conditions": result.get("predicted_conditions", []),
        "sources": [d["topic"] for d in result.get("rag_docs", [])],
        "kg_available": result.get("kg_data", {}).get("available", False),
        "vision_findings": result.get("vision_findings"),
        "vision_error": result.get("vision_error"),
        "ocr_text_extracted": bool(result.get("ocr_text")),
        "ocr_error": result.get("ocr_error"),
    }


if __name__ == "__main__":
    print(run_pipeline("test_session", "I have severe chest pain and difficulty breathing"))
    print("---")
    print(run_pipeline("test_session", "I have fever and body aches for two days"))
    print("---")
    # Vision path smoke test (will hit vision_error since no OPENAI_API_KEY / no network here —
    # confirms the graceful-degradation path itself works, not the real vision call)
    print(run_pipeline("test_session", "What does this rash look like?", image_b64="ZmFrZV9pbWFnZV9ieXRlcw=="))
