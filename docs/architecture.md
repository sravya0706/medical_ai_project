# MediAssist — Current System Architecture

This document describes the code that is currently implemented. For a slower, beginner-oriented explanation of ingestion and request scenarios, see [onboarding_code_and_scenarios.md](./onboarding_code_and_scenarios.md).

## 1. System overview

MediAssist is a React + FastAPI medical-assistant demo. A protected text-chat or image-upload request is passed through a LangGraph workflow. The workflow checks emergency patterns first, then combines rule-based symptom extraction, an XGBoost classifier, RAG retrieval from ChromaDB, optional Neo4j enrichment, session memory, and an OpenAI model response.

```text
React frontend
  │ Axios + Bearer JWT
  ▼
FastAPI routes
  │ validate request + identify user
  ├─ POST /api/v1/chat
  └─ POST /api/v1/vision/upload
  ▼
LangGraph pipeline
  │
  ├─ Guardrail check ── high risk ──> fixed emergency response
  │
  └─ safe request
       ├─ image only: OCR + PII redaction → document text or Vision
       └─ NLP → ML classifier → RAG → optional Neo4j → memory → prompt → Chat LLM
  ▼
Session memory + optional MongoDB persistence
  ▼
JSON response to frontend
```

## 2. Expanded end-to-end architecture diagram

```text
┌───────────────────────────────────────────────────────────────────────┐
│                           React Frontend                               │
│ Login / Register · Text Chat · Image Upload · History Sidebar          │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │ Axios
                                    │ Authorization: Bearer <JWT>
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                           FastAPI (`app/main.py`)                      │
│ CORS middleware · route registration · Mongo startup/index check       │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
              ┌─────────────────────┼──────────────────────┐
              ▼                     ▼                      ▼
     ┌────────────────┐   ┌────────────────────┐  ┌────────────────────┐
     │ Auth routes    │   │ Chat route         │  │ Vision upload route│
     │ register/login │   │ POST /api/v1/chat  │  │ POST /vision/upload│
     └───────┬────────┘   └─────────┬──────────┘  └─────────┬──────────┘
             │                      │                       │
             ▼                      │                       ▼
     ┌────────────────┐              │          ┌──────────────────────┐
     │ MongoDB users  │              │          │ File validation      │
     │ + signed JWT   │              │          │ JPEG/PNG · ≤10 MB    │
     └────────────────┘              │          │ Base64 encode        │
                                     │          └──────────┬───────────┘
                                     │                     │
                                     └──────────┬──────────┘
                                                ▼
                              ┌──────────────────────────────────┐
                              │ In-process session memory         │
                              │ store user turn by session_id      │
                              └────────────────┬─────────────────┘
                                               ▼
              ┌──────────────────────────────────────────────────────┐
              │ LangGraph workflow + conditional (agentic) routing    │
              │            (`agents/orchestrator.py`)                 │
              └──────────────────────────────┬───────────────────────┘
                                             ▼
                              ┌──────────────────────────────────┐
                              │ 1. Guardrail + conditional router │
                              │ high risk → END; image → OCR;     │
                              │ otherwise → NLP                   │
                              └──────────────┬───────────┬─────────┘
                                  high risk  │           │ safe
                                             ▼           ▼
                         ┌────────────────┐    ┌─────────────────────────┐
                         │ Fixed emergency│    │ Image supplied?         │
                         │ response + END │    └───────────┬─────────────┘
                         └────────────────┘          yes   │   no
                                                   ┌────────▼──────────────┐  │
                                                   │ 2. OCR + PII redaction│  │
                                                   │ Tesseract; redacted   │  │
                                                   │ text only             │  │
                                                   └─────┬──────────────────┘  │
                                                         │ OCR text?           │
                                          text found ────┤──── none            │
                                                         ▼                     │
                                           ┌───────────────────────────┐       │
                                           │ 3. Vision (non-document)  │       │
                                           │ GPT-4o findings            │       │
                                           └─────────────┬─────────────┘       │
                                                         ▼                     │
                              ┌──────────────────────────────────┐
                              │ 4. NLP symptom extraction         │
                              │ phrase → binary symptom flags     │
                              └────────────────┬─────────────────┘
                                               ▼
                              ┌──────────────────────────────────┐
                              │ 5. XGBoost classifier             │
                              │ top 3 possible conditions         │
                              └────────────────┬─────────────────┘
                                               ▼
                              ┌──────────────────────────────────┐
                              │ 6. RAG retrieval                  │
                              │ TF-IDF → ChromaDB → top 4 chunks  │
                              │ (chunks prepared by LangChain)    │
                              └────────────────┬─────────────────┘
                                               ▼
                              ┌──────────────────────────────────┐
                              │ 7. Neo4j enrichment (optional)    │
                              │ condition → meds/specialists      │
                              └────────────────┬─────────────────┘
                                               ▼
                              ┌──────────────────────────────────┐
                              │ 8. Recent session history         │
                              │ last 6 turns                      │
                              └────────────────┬─────────────────┘
                                               ▼
                              ┌──────────────────────────────────┐
                              │ 9. Prompt Builder                 │
                              │ history + RAG + ML + KG + query   │
                              └────────────────┬─────────────────┘
                                               ▼
                              ┌──────────────────────────────────┐
                              │ 10. OpenAI Chat LLM               │
                              │ gpt-4o-mini → final response      │
                              └────────────────┬─────────────────┘
                                               ▼
                              ┌──────────────────────────────────┐
                              │ Store assistant turn              │
                              │ Persist conversation in MongoDB   │
                              │ (when MongoDB is available)       │
                              └────────────────┬─────────────────┘
                                               ▼
                                  JSON `ChatResponse` to React
```

**Data stores supporting the flow**

| Store | Used by | Purpose |
|---|---|---|
| MongoDB | Auth, chat/history routes | Users and durable conversations. |
| Process memory | Memory pipeline node | Recent turns used in the current server process. |
| ChromaDB | RAG node | Persisted medical-document chunks and vectors. |
| Neo4j | KG node | Optional disease, symptom, medication, and specialist relationships. |
| Local `data/` artifacts | ML/RAG nodes | XGBoost model, label encoder, feature order, TF-IDF vectorizer. |

### Active document OCR and PII-redaction path

Document-like image uploads now use this implemented request-time path:

```text
JPEG/PNG upload
  ↓
Tesseract OCR (`extract_text_from_image`)
  ↓
Raw extracted text
  ↓
Regex PII redaction (`redact_pii`)
  ├─ phone number → [REDACTED_PHONE]
  ├─ Aadhaar-like ID → [REDACTED_ID]
  └─ email → [REDACTED_EMAIL]
  ↓
Redacted text merged into the LangGraph query for NLP, RAG, and the final LLM
```

`ocr_node()` in `app/agents/orchestrator.py` decodes the uploaded image in memory and calls `process_document_bytes()` in `app/ocr/ocr_pii.py`. Only the redacted OCR text is merged into the downstream query; raw OCR text is not sent to RAG or the LLM and is not logged or persisted. If OCR returns readable text, the graph treats the upload as a report/prescription and skips Vision. If OCR returns no text or fails, the graph uses the existing Vision path for image analysis instead.

### Where LangGraph and LangChain are used

```text
Request-time orchestration
  LangGraph StateGraph
    └─ guardrail conditional edge
         ├─ emergency → END
         ├─ image → vision node
         └─ text → NLP node
    └─ sequential shared-state nodes after routing

Offline RAG ingestion
  LangChain RecursiveCharacterTextSplitter
    └─ split knowledge-base documents into overlapping chunks
    └─ TF-IDF embedding + ChromaDB upsert
```

- **LangGraph** is actively used at request time in `app/agents/orchestrator.py`. Its `StateGraph` carries one shared `WorkflowState` between nodes and `route_after_guardrail()` chooses the path. This is the project’s current agentic/conditional routing. It is rule-based routing, not an LLM autonomously deciding which tools to call.
- **LangChain** is currently used in `app/rag/ingest.py` through `RecursiveCharacterTextSplitter` to prepare RAG chunks. The current runtime prompt and OpenAI calls are implemented directly in `app/prompt_builder.py` and `app/llm/openai_client.py`; they do not use LangChain chains or `langchain-openai`.

## 3. Implemented HTTP API

`app/main.py` registers the following route modules:

| Endpoint | Auth | Implementation | Purpose |
|---|---:|---|---|
| `GET /health` | No | `app/main.py` | Reports API health and Mongo availability. |
| `POST /api/v1/auth/register` | No | `app/routes/auth_routes.py` | Creates a MongoDB user and returns a JWT. |
| `POST /api/v1/auth/login` | No | `app/routes/auth_routes.py` | Verifies credentials and returns a JWT. |
| `POST /api/v1/chat` | Yes | `app/routes/chat_routes.py` | Runs the text pipeline. |
| `POST /api/v1/vision/upload` | Yes | `app/routes/vision_routes.py` | Validates a JPEG/PNG, then runs the image pipeline. |
| `GET /api/v1/history` | Yes | `app/routes/chat_routes.py` | Lists the current user's conversations. |
| `GET /api/v1/history/{id}` | Yes | `app/routes/chat_routes.py` | Fetches one conversation only when it belongs to the current user. |

The React service functions in `frontend/src/services/` call these endpoints. The Axios interceptor in `frontend/src/services/api.js` automatically attaches the JWT stored in `localStorage`.

## 4. Authentication and persistence

```text
Register/login
  → MongoDB user record
  → signed JWT containing user ID
  → frontend stores token
  → Axios sends Authorization: Bearer <token>
  → FastAPI dependency decodes token before protected route runs
```

- Password hashing, verification, and JWT creation live in `app/auth/security.py`.
- `app/auth/dependencies.py:get_current_user_id()` rejects invalid/expired tokens with `401`.
- `app/db/mongo_client.py` stores `users` and `conversations` collections.
- A conversation contains a title, owner `userId`, message array, and timestamps.
- The `/chat` and `/vision/upload` routes use `session_id` to reuse the same MongoDB conversation during a browser session.

MongoDB persistence is best effort for chat requests. When MongoDB is unavailable, auth and history endpoints return `503`, while the AI pipeline can still return an answer without saving it.

## 5. LangGraph request workflow

The workflow is defined in `app/agents/orchestrator.py`. `run_pipeline()` creates a `WorkflowState` and invokes the compiled LangGraph graph.

### 5.1 Text request path

```text
POST /api/v1/chat
  ↓
chat_routes.chat()
  ↓
session_memory.add_turn(user message)
  ↓
run_pipeline(session_id, message)
  ↓
guardrail_check
  ↓ safe
nlp → classify → rag → kg → memory → generate → END
  ↓
store assistant turn + append messages to MongoDB
  ↓
ChatResponse
```

### 5.2 Image request path

```text
POST /api/v1/vision/upload
  ↓
validate_and_encode_image()
  ├─ JPEG/PNG content type check
  ├─ 10 MB maximum size check
  └─ Base64 encoding
  ↓
run_pipeline(session_id, message, image_b64)
  ↓
guardrail_check
  ↓ safe
ocr → OCR text? ── yes → nlp → classify → rag → kg → memory → generate → END
              └─ no/failure → vision → nlp → classify → rag → kg → memory → generate → END
  ↓
store assistant turn + append messages to MongoDB
  ↓
ChatResponse
```

### 5.3 Guardrail-first routing

Guardrails run **before the LLM**, not after it. `guardrail_check` is the graph entry point.

```text
guardrail_check
  ├─ high-risk phrase found → END
  ├─ image supplied → vision
  └─ otherwise → nlp
```

`app/guardrails/safety.py` performs deterministic phrase matching for high-risk patterns such as chest pain, difficulty breathing, severe bleeding, stroke signs, seizures, and self-harm language. A match produces a fixed emergency-care message and skips Vision, NLP, ML, RAG, Neo4j, prompt construction, and the OpenAI call.

This order is intentional: emergency escalation must not depend on LLM judgment, and there is no need to spend time or API cost on later stages when the response is already known.

## 6. Pipeline component responsibilities

| Stage | Code | Input | Output | Notes |
|---|---|---|---|---|
| Guardrail | `app/guardrails/safety.py` | Raw query | Emergency message or `None` | First graph node. |
| OCR + PII redaction | `app/ocr/ocr_pii.py` | Uploaded image bytes | Redacted report text | Runs first for every image; readable text skips Vision and continues to NLP/RAG. |
| Vision | `app/llm/openai_client.py` | Base64 image + user text | Structured visible findings | Runs only when OCR finds no readable document text; failures fall back to text-only processing. |
| NLP | `app/nlp/extractor.py` | Query, including image findings when available | Binary symptom flags, matched phrases, duration | Rule/phrase matching; not trained NER. |
| Classification | `app/ml/predict.py` | Symptom flags | Top three possible conditions and confidences | Skips if no symptoms were extracted. |
| RAG | `app/rag/retriever.py` | Query | Up to four medical chunks | Uses local TF-IDF vectors with ChromaDB. |
| Knowledge graph | `app/kg/neo4j_client.py` | Top predicted condition | Medications, specialists, symptoms | Optional; skips if there is no prediction or Neo4j is unavailable. |
| Memory | `app/memory/session_memory.py` | Session ID | Last six turns as text | Process-local; not durable or multi-instance safe. |
| Prompt builder | `app/prompt_builder.py` | Query, history, RAG docs, ML results, KG data | System + user chat messages | Instructs the model not to diagnose or invent facts. |
| Generation | `app/llm/openai_client.py` | Prompt messages | Final assistant response | Uses `gpt-4o-mini` by default. |

## 7. Data preparation / ingestion

These jobs are separate from serving requests and create artifacts the runtime pipeline loads.

```text
Synthetic disease profiles → CSV → XGBoost artifacts
Knowledge-base documents → chunks → TF-IDF vectors → ChromaDB
Cypher seed statements → Neo4j disease relationship graph
```

| Job | Command | Output |
|---|---|---|
| Generate dataset | `python -m app.ml.generate_dataset` | `data/symptom_disease_dataset.csv` |
| Train classifier | `python -m app.ml.train` | `model.pkl`, `label_encoder.pkl`, `model_columns.json`, `metrics.json` |
| Ingest RAG docs | `python -m app.rag.ingest` | `tfidf_vectorizer.pkl` and `data/chroma_db/` |
| Seed graph | `python -m app.kg.seed_data` | Disease/symptom/medication/specialist nodes in Neo4j |

### Classifier

`app/ml/generate_dataset.py` generates a synthetic, binary symptom dataset for ten conditions. `app/ml/train.py` uses an 80/20 stratified split, trains an `XGBClassifier`, evaluates it, and serializes the model artifacts. The classifier is a demo component and must not be represented as clinically validated.

### RAG

`app/rag/knowledge_base.py` supplies 11 educational documents. `app/rag/ingest.py` chunks each document using a 500-character chunk size and 100-character overlap, fits a local TF-IDF vectorizer on the chunks, and upserts chunks plus `{topic, source_id}` metadata into the persistent Chroma collection `medical_docs`.

### Knowledge graph

`app/kg/seed_data.py` seeds selected diseases using idempotent Cypher `MERGE` commands. For example, it models `Influenza → HAS_SYMPTOM → Fever` and `Influenza → TREATED_BY → Paracetamol`.

## 8. Prompt and response shape

`app/prompt_builder.py` combines:

1. recent session history;
2. retrieved RAG medical context;
3. top classifier predictions;
4. available Neo4j relationships; and
5. the current user query.

The system prompt directs the model to use supplied context, avoid unsupported claims, avoid definitive diagnoses, and recommend professional care where appropriate.

The text and image routes return `ChatResponse` from `app/schemas.py`:

```json
{
  "success": true,
  "response": "...",
  "escalated": false,
  "predicted_conditions": [
    {"condition": "Migraine", "confidence": 0.7723}
  ],
  "sources": ["Migraine", "Viral Fever"],
  "error": null
}
```

## 9. Graceful-degradation behavior

| Dependency/state | Current behavior |
|---|---|
| MongoDB unavailable | Auth/history return `503`; chat response is returned but not persisted. |
| Neo4j unavailable | Log warning and continue with `available=False` KG data. |
| OCR unavailable | Record `ocr_error` and continue to the Vision path. |
| Vision unavailable | Record `vision_error` and continue with the original text query. |
| OpenAI unavailable or API key missing | Final text generation fails clearly; `/chat` returns `503`. |
| Empty ChromaDB collection | RAG returns an empty list; prompt says no relevant document was retrieved. |
| No extracted symptoms | Classifier and KG skip; RAG and LLM generation still run. |

## 10. Current limitations and intentionally unimplemented paths

- The system currently accepts JPEG/PNG uploads only. OCR and PII redaction are active for those image uploads, but there is no PDF report endpoint yet.
- PII redaction is regex-based and covers phone numbers, Aadhaar-like IDs, and email addresses. It does not reliably detect names or every possible sensitive field.
- Image validation trusts the client-provided content type; it does not inspect file signatures.
- NLP is a fixed symptom lexicon. If a vision finding does not use one of those exact phrases, ML classification will skip.
- `needs_followup()` exists in `app/nlp/extractor.py` but is not connected to the LangGraph routing logic.
- Conversation memory is an in-process dictionary and is lost on restart; MongoDB history is persistent but does not provide live prompt memory after a restart.
- The RAG knowledge base and ML dataset are educational/demo assets, not clinical sources or clinical validation.

## 11. Operational tracing

The console prints added to the code use stage labels such as `[chat]`, `[pipeline]`, `[nlp]`, `[ml]`, `[rag]`, `[KG]`, `[memory]`, `[llm]`, and `[history]`. Together they show the exact path selected for a request, whether a component was skipped, and whether persistence or a fallback occurred.
