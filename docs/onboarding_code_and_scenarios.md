# MediAssist: Code-Level Onboarding and Request Scenarios

This is the practical guide for understanding the project. Read it with the code open. It explains what data is prepared before the server starts, then exactly what happens for each request type.

> Important: this is a local/demo healthcare assistant. The classifier is trained on synthetic data, the RAG content is a small educational knowledge base, and model predictions are possible conditions—not diagnoses.

## 1. What is stored where?

| Store | What it contains | Created/filled by | Used during |
|---|---|---|---|
| `data/symptom_disease_dataset.csv` | Symptom flags and disease labels | `app/ml/generate_dataset.py` | Model training only |
| `data/model.pkl` | Trained XGBoost classifier | `app/ml/train.py` | Text/image request classification |
| `data/label_encoder.pkl` | Numeric class → disease-name mapping | `app/ml/train.py` | Turning classifier outputs into names |
| `data/model_columns.json` | Required order of the 15 symptom columns | `app/ml/train.py` | Creating a prediction input row |
| `data/tfidf_vectorizer.pkl` | Fitted local TF-IDF vectorizer | `app/rag/ingest.py` | Embedding the incoming query |
| `data/chroma_db/` | RAG document chunks and their vectors | `app/rag/ingest.py` | Finding relevant medical context |
| Neo4j | Disease/symptom/medication/specialist relationships | `app/kg/seed_data.py` | Optional structured enrichment |
| MongoDB | Users and chat conversations | API routes while the app runs | Login and chat history |
| Process memory | Last six chat turns per `session_id` | `app/memory/session_memory.py` | Conversation context in the prompt |

## 2. One-time data ingestion/setup flow

Run these before testing the full app:

```bash
source venv/bin/activate
python -m app.ml.generate_dataset
python -m app.ml.train
python -m app.rag.ingest
python -m app.kg.seed_data   # requires Neo4j to be running
```

MongoDB and Neo4j are typically started with:

```bash
docker compose up -d
```

### 2.1 Building the ML classifier

Relevant code:

- `app/ml/generate_dataset.py`
- `app/ml/train.py`
- `app/ml/predict.py`

Flow:

```text
DISEASE_PROFILES
  └─ Example: Migraine → headache, nausea, dizziness
        ↓
generate_row() makes one row of 0/1 symptom flags
        ↓
build_dataset() makes 150 rows per disease and writes CSV
        ↓
train() reads CSV
        ↓
X = all symptom columns; y = Disease column
        ↓
LabelEncoder turns disease names into class numbers
        ↓
80/20 stratified train/test split
        ↓
XGBClassifier.fit(X_train, y_train)
        ↓
Save model, label encoder, column order, and metrics
```

The classifier has no natural-language understanding. It only receives a row like this:

```python
{
    "fever": 0,
    "cough": 0,
    "headache": 1,
    "nausea": 0,
    # ... remaining 11 symptom fields
}
```

Later, `extract_symptoms()` creates the flags and `predict_conditions()` builds the DataFrame in the saved `model_columns.json` order. XGBoost returns probabilities; the code returns the top three conditions.

### 2.2 Building the RAG knowledge base

Relevant code:

- `app/rag/knowledge_base.py`
- `app/rag/ingest.py`
- `app/rag/retriever.py`

Flow:

```text
DOCUMENTS: 11 Python dictionaries
  └─ each has id, topic, text
        ↓
RecursiveCharacterTextSplitter
  └─ chunk size: 500 characters; overlap: 100 characters
        ↓
All chunks are passed to TfidfVectorizer.fit()
        ↓
Fitted vectorizer is saved to data/tfidf_vectorizer.pkl
        ↓
Each chunk gets:
  id        = "<document-id>_chunk<index>"
  document  = chunk text
  metadata  = {topic, source_id}
        ↓
ChromaDB collection "medical_docs" receives an upsert
```

Example stored RAG record:

```python
{
    "id": "migraine_overview_chunk0",
    "document": "A migraine is a neurological condition...",
    "metadata": {"topic": "Migraine", "source_id": "migraine_overview"}
}
```

Why `upsert` instead of `add`? You can run ingestion again after changing knowledge-base text without creating duplicate records.

This project uses TF-IDF because it works completely locally. It is not an OpenAI embedding model. Changing to a hosted or sentence-transformer embedding later requires rebuilding the Chroma collection with the new embedding method.

### 2.3 Building the knowledge graph

Relevant code:

- `app/kg/seed_data.py`
- `app/kg/neo4j_client.py`

`SEED_CYPHER` contains Neo4j `MERGE` instructions. `MERGE` means “find it if it already exists; otherwise create it.”

```text
(Disease: Influenza)
   ├─ HAS_SYMPTOM → (Symptom: Fever)
   ├─ HAS_SYMPTOM → (Symptom: Cough)
   ├─ TREATED_BY → (Medication: Paracetamol)
   └─ REQUIRES_SPECIALIST → (Specialist: General Physician)
```

At request time, `get_related_entities(top_condition)` runs three Cypher queries for medication, specialist, and known symptoms. Neo4j is optional: connection failures return an empty result with `available=False`, so the user can still receive a RAG-grounded response.

## 3. Server startup and frontend entry point

```text
Browser
  ↓ React services (`frontend/src/services/*.js`)
Axios adds: Authorization: Bearer <JWT>
  ↓
FastAPI (`app/main.py`)
  ├─ CORS middleware
  ├─ auth routes
  ├─ chat/history routes
  └─ vision upload route
```

Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

The frontend uses these real endpoints:

| User action | Frontend function | Backend endpoint |
|---|---|---|
| Register | `authService.register()` | `POST /api/v1/auth/register` |
| Login | `authService.login()` | `POST /api/v1/auth/login` |
| Send text | `chatService.sendMessage()` | `POST /api/v1/chat` |
| Upload image | `chatService.sendImage()` | `POST /api/v1/vision/upload` |
| Load sidebar history | `historyService.getConversations()` | `GET /api/v1/history` |

## 4. Scenario A: normal text chat

Example user message: **“I have a headache.”**

### The exact route and function chain

```text
POST /api/v1/chat
  ↓
app/routes/chat_routes.py → chat(payload, user_id)
  ↓
get_current_user_id() validates the JWT
  ↓
session_memory.add_turn(session_id, "user", message)
  ↓
orchestrator.run_pipeline(session_id, message)
  ↓
LangGraph workflow:
  guardrail → nlp → classify → rag → kg → memory → generate
  ↓
chat route stores assistant turn and persists both turns in MongoDB
  ↓
ChatResponse JSON → frontend
```

### What each component does

1. **Request validation** — FastAPI validates the body using `ChatRequest` from `app/schemas.py`. It requires `message` and accepts a `session_id`.

2. **Authentication** — `get_current_user_id()` in `app/auth/dependencies.py` reads the bearer token and returns the user ID encoded in its JWT. Invalid or expired tokens give `401` before the pipeline starts.

3. **Session memory** — `add_turn()` saves the original message in the in-process `_sessions` dictionary. This memory is separate from MongoDB and is used immediately to supply recent chat context to the LLM.

4. **Guardrail** — `guardrail_node()` calls `apply_guardrail()`. It checks direct high-risk phrases such as `chest pain`, `difficulty breathing`, or `seizure`. For a headache, it returns `None`, so the graph continues.

5. **NLP extraction** — `nlp_node()` calls `extract_symptoms()` from `app/nlp/extractor.py`. This is phrase matching, not an NER model. The word `headache` creates:

   ```python
   {
       "symptoms": {"headache": 1},
       "matched_phrases": ["headache"],
       "duration": None
   }
   ```

6. **ML classification** — `classify_node()` sends `{"headache": 1}` to `predict_conditions()`. Missing symptom keys become zero. The XGBoost model might return Migraine, COVID-19, and Viral Fever, each with a confidence value.

7. **RAG retrieval** — `rag_node()` calls `retrieve(original_query)`. The query is embedded with the saved TF-IDF vectorizer. ChromaDB returns the nearest four chunks, including their `topic`, `text`, and distance.

8. **Knowledge graph** — `kg_node()` takes the *first* ML prediction, such as `Migraine`, and asks Neo4j for its relationships. Note that the seed graph currently only has selected diseases. A successful Neo4j connection can still return no relationships for an unseeded disease.

9. **Recent conversation context** — `memory_node()` calls `get_recent_history_text()`. It includes up to six turns (the last three user/assistant pairs) in the LLM prompt.

10. **Prompt + LLM** — `generate_node()` calls `build_messages()` with the user query, recent history, retrieved chunks, predictions, and graph data. `generate_response()` sends the two built messages to `gpt-4o-mini`.

11. **Persistence + response** — `chat()` saves the assistant response to session memory. If MongoDB is available, it creates/reuses one conversation for the session and appends user and assistant messages. Finally, FastAPI returns `ChatResponse` with response text, predictions, sources, and escalation status.

### How to read the console output

```text
[chat] Request received                 HTTP route received an authenticated request
[memory] Stored user turn               In-process context updated
[pipeline][guardrail] Passed            No emergency phrase found
[nlp] Extraction complete               Rule-based symptoms found
[ml] Prediction complete                XGBoost results calculated
[rag] Retrieval complete                ChromaDB documents selected
[kg] Completed                          Neo4j lookup attempted/completed
[prompt] Built                          All upstream data combined
[llm] Chat response received            OpenAI returned text
[history] Conversation persisted        MongoDB append succeeded
[chat] Response ready                   HTTP 200 response is about to return
```

## 5. Scenario B: emergency text

Example: **“I have chest pain and difficulty breathing.”**

```text
chat route → memory → guardrail
                         ↓
                 high-risk phrase matched
                         ↓
                       END
                         ↓
               emergency response returned
```

`route_after_guardrail()` returns `"escalate"`, which LangGraph maps directly to `END`. The following components deliberately do **not** run:

- NLP extraction
- XGBoost classification
- RAG retrieval
- Neo4j query
- prompt construction
- OpenAI call

This is intentional: if the predefined emergency message is required, there is no reason to spend time or money on downstream processing. The emergency response is still added to memory and MongoDB by the chat route.

## 6. Scenario C: image upload

Example: upload `sample_lab_report.jpg` with **“Can you explain this report?”**

```text
POST /api/v1/vision/upload (multipart/form-data)
  ↓
validate_and_encode_image()
  ├─ accept JPEG/PNG content type
  ├─ enforce 10 MB limit
  └─ base64 encode bytes
  ↓
run_pipeline(session_id, message, image_b64)
  ↓
guardrail → OCR + PII redaction → OCR text? → nlp → classify → rag → kg → memory → generate
                                         └─ no text/failure → vision → nlp → classify → rag → kg → memory → generate
```

### What differs from normal chat?

1. `vision_routes.upload_image()` accepts `file`, `message`, and `session_id` as multipart form fields.
2. `validate_and_encode_image()` validates the declared MIME type and size, then Base64-encodes the image. The endpoint accepts JPEG/PNG, not PDF, and does not yet verify file signature bytes.
3. The guardrail runs **before** image processing. A high-risk typed message exits before OCR or vision analysis.
4. `ocr_node()` decodes the image in memory, runs Tesseract OCR, and redacts phone numbers, Aadhaar-like IDs, and emails using `process_document_bytes()`. Only redacted text can proceed to NLP, RAG, and the final LLM.
5. If OCR finds readable text, the image is treated as a report/prescription and goes directly to NLP/RAG. Vision is skipped so raw document content is not sent to the Vision model.
6. If OCR finds no readable text or fails, `vision_node()` passes the Base64 image plus user text to `analyze_medical_image()` using `gpt-4o`. Vision returns structured visible findings, appended internally to the query:

   ```text
   Can you explain this report?

   [Image findings: <vision model output>]
   ```

7. The redacted OCR text or Vision findings go to NLP, RAG, and the final prompt. The user’s original text—not the internal enrichment block—is stored as their message in history.

### Why did your earlier image log skip classifier and KG?

Your run showed:

```text
[nlp] Extraction complete (symptoms=[], matched=[], duration=None)
[classify] Skipped: no symptoms extracted
[kg] Skipped: no predicted condition
```

That run occurred before OCR was connected. The vision call succeeded, but the rule-based extractor only recognizes phrases in `SYMPTOM_LEXICON`. The Vision model’s findings did not contain an exact supported phrase, so it produced no binary symptom flags. RAG and final LLM generation still ran because they work with free text; only ML and KG need extracted symptoms/predicted disease names.

If vision fails because the API key is missing or the service is unavailable, `vision_node()` records `vision_error` and continues through the text-only path instead of failing the entire request.

## 7. Scenario D: login and chat history

### Registration/login

```text
POST /api/v1/auth/register or /login
  ↓
MongoDB availability check
  ↓
register: hash password and insert user
login: fetch user and verify password hash
  ↓
create_access_token(user_id)
  ↓
return JWT to frontend
  ↓
frontend saves JWT in localStorage
  ↓
Axios interceptor attaches it to future API calls
```

### History retrieval

```text
GET /api/v1/history
  ↓
JWT dependency returns user_id
  ↓
MongoDB query: conversations for that user, newest first
  ↓
return conversation list
```

The chat route uses `session_id → conversation_id` mapping in `app/memory/conversation_map.py`. This lets multiple messages from the same session append to the same MongoDB conversation.

## 8. What happens when a dependency is unavailable?

| Missing dependency | Result |
|---|---|
| MongoDB | Login/register/history return `503`; chat pipeline can still generate an answer but does not persist history. |
| Neo4j | Pipeline continues; KG data is empty with `available=False`. |
| OpenAI API key | Text generation returns a clear error, surfaced as `503` from `/chat`. Vision degrades to text-only, but final text generation still needs an API key. |
| OpenAI network/service error | Same as API-key failure for final generation; vision failure alone falls back to text-only. |
| Empty ChromaDB collection | RAG returns no documents; prompt explicitly says that no relevant context was retrieved. |
| Invalid JWT | Request ends with `401` before chat/image processing. |
| Unsupported image type or image above 10 MB | Upload ends with `400` before the pipeline starts. |

## 9. Important implementation facts for a new developer

- `needs_followup()` exists in `app/nlp/extractor.py`, but it is **not wired into the current LangGraph workflow**. One extracted symptom therefore still goes to ML, as your headache test demonstrated.
- The current image endpoint accepts JPEG and PNG only. It now runs OCR and regex PII redaction first; when readable report text exists, it uses that redacted text for RAG/LLM processing and skips Vision. PDF upload is not implemented yet.
- The historical `docs/overview.md` mentions endpoints such as `/api/symptoms` and `/api/reports`. Those are not the current implemented endpoints. Use the endpoint table in section 3 of this document and `app/main.py` as the source of truth.
- In-process session memory disappears on server restart and is not shared between multiple backend instances. MongoDB history persists separately.
- Console logs intentionally report stage results and sizes rather than raw message contents.

## 10. Recommended code-reading order

1. `app/main.py` — application creation and route registration.
2. `app/routes/chat_routes.py` — normal chat HTTP flow.
3. `app/agents/orchestrator.py` — the actual LangGraph pipeline and routing.
4. `app/nlp/extractor.py`, `app/ml/predict.py`, `app/rag/retriever.py`, `app/kg/neo4j_client.py` — individual pipeline stages.
5. `app/prompt_builder.py` and `app/llm/openai_client.py` — how the final LLM request is created.
6. `app/routes/vision_routes.py` and `app/routes/upload_validation.py` — image-specific flow.
7. `app/db/mongo_client.py`, `app/auth/`, and `app/memory/` — user identity and persistence.
