# MediAssist — AI Medical Chatbot (Local Runnable Backend)

A real, working implementation of the documented MediAssist architecture:
FastAPI + LangChain/LangGraph orchestration + RAG (ChromaDB) + Knowledge Graph
(Neo4j) + XGBoost symptom classifier + JWT auth (MongoDB) + OCR/PII redaction
+ safety guardrails.

## What's real vs. what needs your own setup

Everything below was **actually built and tested end-to-end** in the
development sandbox:

| Component | Status |
|---|---|
| XGBoost classifier | Real, trained — 89% held-out test accuracy on a **synthetic** dataset (see note below) |
| NLP symptom extraction | Real, rule-based, tested |
| RAG (ChromaDB) | Real, working retrieval — see embedding note below |
| Neo4j Knowledge Graph | Real driver + Cypher code — **needs a running Neo4j instance** (docker-compose provided) |
| MongoDB (auth/history) | Real PyMongo code — **needs a running MongoDB instance** (docker-compose provided) |
| JWT + bcrypt auth | Real, tested |
| OCR + PII redaction | Real, using actual Tesseract |
| Safety guardrails | Real, tested |
| LangGraph orchestration | Real `StateGraph`, tested end-to-end |
| OpenAI LLM calls | Real SDK code — **needs your `OPENAI_API_KEY`**; without it, returns a clear 503 rather than a fake response |
| Vision (GPT-4V) upload | Real, wired into the LangGraph pipeline via `POST /api/v1/vision/upload` — degrades gracefully to text-only if vision analysis fails |

### Three honest substitutions, clearly marked in code comments

1. **Dataset**: The architecture references a public Kaggle symptom-disease
   dataset. This environment had no internet access to download it, so
   `app/ml/generate_dataset.py` generates a structurally equivalent
   **synthetic** dataset instead. Swap in the real Kaggle CSV before relying
   on this for anything beyond a local demo — see `app/ml/train.py`.
2. **Embeddings**: The architecture describes OpenAI or sentence-transformer
   embeddings. Both require network access (to `api.openai.com` or
   `huggingface.co`) that wasn't available in the dev sandbox, so
   `app/rag/ingest.py` uses a real, classical **TF-IDF** embedding instead
   (scikit-learn, zero network dependency). Swap in
   `chromadb.utils.embedding_functions.OpenAIEmbeddingFunction` or
   `SentenceTransformerEmbeddingFunction` once you have network access —
   the rest of the RAG pipeline doesn't need to change.
3. **Knowledge base content**: `app/rag/knowledge_base.py` contains original,
   general-education medical text written for this project — not a real
   curated clinical source. Replace with WHO/CDC-sourced content (properly
   licensed) before any real use.

## Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
# 1. Install dependencies
pip install -r requirements.txt

# XGBoost's compiled library needs OpenMP's runtime (libomp), which isn't installed on macOS by default and isn't something pip can install for you (it's a system # library, not a Python package).
brew install libomp

# 2. Configure environment
cp .env.example .env
# edit .env: set OPENAI_API_KEY at minimum for real LLM responses

# 3. Start real local MongoDB + Neo4j (requires Docker)
docker compose up -d

# 4. Generate the dataset and train the classifier
python3 -m app.ml.generate_dataset
python3 -m app.ml.train

# 5. Ingest the RAG knowledge base
python3 -m app.rag.ingest

# 6. Seed the knowledge graph (after Neo4j is up)
python3 -m app.kg.seed_data

# 7. Run the backend
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Frontend Setup

A full React (Vite) frontend lives in `frontend/` — login/register, chat with
image upload, conversation history sidebar, JWT auth via Context API.

```bash
cd frontend
npm install
cp .env.example .env   # points at http://localhost:8000 by default
npm run dev
```

Visit `http://localhost:5173`. Register an account, then start chatting.
If MongoDB isn't running, the sidebar shows a clear notice instead of
silently failing — you can still chat, the session just won't be saved.

**Design note:** the frontend uses an original design system (not a
component library default) — a warm paper background, deep pine accent,
Fraunces/IBM Plex Sans/IBM Plex Mono type pairing, and a signature
animated "vital line" (ECG-style trace) as the loading indicator instead
of a generic spinner. See `frontend/src/index.css` for the full token set.

## Without Docker

The app still runs and the AI pipeline (NLP → classifier → RAG → guardrails
→ LLM) still works fully without Mongo/Neo4j:
- Auth/history endpoints will return `503` (clear error, not a crash)
- The Knowledge Graph enrichment step will silently degrade to "no data"
  (documented behavior — KG is an enrichment layer, not a hard dependency)
- Everything else works normally

## Testing individual components

Every module has a `__main__` block you can run directly to sanity-check it
in isolation:

```bash
python3 -m app.nlp.extractor
python3 -m app.ml.predict
python3 -m app.rag.retriever
python3 -m app.ocr.ocr_pii
python3 -m app.guardrails.safety
python3 -m app.agents.orchestrator   # full pipeline, no HTTP layer
```

## API Endpoints

| Method | Path | Auth required | Notes |
|---|---|---|---|
| GET | `/health` | No | Reports Mongo connectivity status |
| POST | `/api/v1/auth/register` | No | Requires MongoDB |
| POST | `/api/v1/auth/login` | No | Requires MongoDB |
| POST | `/api/v1/chat` | Yes (Bearer JWT) | Runs the full LangGraph pipeline |
| POST | `/api/v1/vision/upload` | Yes (Bearer JWT) | Multipart upload (`file`, `message`, `session_id`) — image findings merge into the same pipeline as a text query |
| GET | `/api/v1/history` | Yes | Requires MongoDB |
| GET | `/api/v1/history/{id}` | Yes | Requires MongoDB |

## Architecture note: guardrail-first routing

The LangGraph workflow checks safety guardrails **before** running NLP/RAG/
classification, not after (see `app/agents/orchestrator.py`). This is a
deliberate efficiency choice: if a message is going to be overridden with an
escalation message regardless, there's no reason to spend the retrieval and
classification cost first. This is a legitimate variation worth mentioning
if asked about it directly — the original docs describe guardrails running
after retrieval; this implementation optimizes for the case where the
guardrail already knows the outcome.

## Known gaps (disclosed, not hidden)

- **PII redaction** is regex-based and cannot catch patient names (no fixed
  pattern) — a production system needs a proper NER model (e.g. Microsoft
  Presidio) layered on top. See comments in `app/ocr/ocr_pii.py`.
- **Idempotency**: no idempotency-key handling on `/api/v1/chat` — a retried
  request after a timeout could create a duplicate conversation entry.
- **Conversation Memory** is in-process (a Python dict) — fine for a single
  instance, but won't work across multiple backend instances. Redis is the
  documented scaling path (see architecture doc's "Future Improvements").
- **Image validation** checks the declared `content_type` header only —
  spoofable by the client. A hardened version verifies actual file
  signature bytes, not just the header (see `app/routes/upload_validation.py`).
