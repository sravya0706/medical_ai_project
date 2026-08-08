"""
Prompt Builder — merges all upstream pipeline outputs into one structured
prompt, matching Module 15/20 exactly.
"""

SYSTEM_PROMPT = (
    "You are an AI Medical Assistant. Answer only using the provided medical "
    "context. If the context is insufficient, say so explicitly instead of "
    "guessing. Do not invent medical facts. Recommend consulting a doctor for "
    "serious symptoms. Never provide a definitive diagnosis — only possible "
    "conditions with appropriate caveats."
)


def build_messages(
    query: str,
    conversation_history: str,
    rag_docs: list[dict],
    predicted_conditions: list[dict],
    kg_data: dict,
) -> list[dict]:
    context_block = "\n\n".join(
        f"[{doc['topic']}] {doc['text']}" for doc in rag_docs
    ) or "No relevant medical documents were retrieved for this query."

    prediction_block = ", ".join(
        f"{c['condition']} ({c['confidence']:.0%} confidence)" for c in predicted_conditions
    ) or "No confident prediction available."

    kg_block = "No additional structured relationship data available."
    if kg_data.get("available"):
        parts = []
        if kg_data.get("medications"):
            parts.append(f"Common medications: {', '.join(kg_data['medications'])}")
        if kg_data.get("specialists"):
            parts.append(f"Relevant specialists: {', '.join(kg_data['specialists'])}")
        if parts:
            kg_block = " | ".join(parts)

    user_message = f"""Conversation so far:
{conversation_history or '(no prior turns in this session)'}

Retrieved medical context:
{context_block}

Classifier-predicted possible conditions:
{prediction_block}

Knowledge graph relationships:
{kg_block}

Patient's current message: {query}
"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
