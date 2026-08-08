# MediAssist — Technologies & Libraries Reference
## Quick Table + Expanded Q&A

---

## Quick Reference Table

| Technology / Library | Category | Purpose in Project |
|---|---|---|
| FastAPI | Backend Framework | REST API server, async request handling |
| Uvicorn | ASGI Server | Runs the FastAPI app |
| Pydantic | Validation | Request/response schema validation |
| LangChain | AI Orchestration | Prompt templates, retrievers, LLM integration |
| LangGraph | AI Orchestration | Multi-agent workflow routing, shared state |
| OpenAI Python SDK | LLM Provider | ChatGPT API calls, GPT-4V (Vision) calls |
| ChromaDB | Vector Database | Stores embeddings, powers RAG retrieval |
| langchain_chroma / langchain_openai | Integration | Connects LangChain to Chroma + OpenAI embeddings |
| Neo4j (Python driver) | Graph Database | Knowledge graph — symptom/disease/medication relationships |
| XGBoost | ML Model | Symptom classification (~85% accuracy) |
| scikit-learn | ML Utilities | Train/test split, accuracy/precision/recall/F1 |
| pandas / numpy | Data Handling | Loading and transforming the symptom-disease dataset |
| joblib | Model Persistence | Save/load the trained XGBoost model |
| pytesseract (Tesseract) | OCR | Extracts text from scanned prescriptions/reports |
| re (regex) | PII Redaction | Masks phone numbers, IDs, etc. before embedding |
| PyMongo | Database Driver | MongoDB access — users, conversations, messages |
| python-jose | Authentication | JWT creation and verification |
| passlib (bcrypt) | Security | Password hashing |
| React | Frontend | Chat UI, auth screens, history, uploads |
| Axios | Frontend HTTP | API calls from React to FastAPI backend |
| React Context API | State Management | User, JWT, conversation, messages |
| pytest | Testing | Unit tests for services/pipeline nodes |

---

## Expanded Q&A — One Section Per Technology

### FastAPI
**Q: Why FastAPI over Flask or Django?**
A: FastAPI gives async support out of the box, which matters because most requests here spend time waiting on external calls (OpenAI, ChromaDB, Neo4j) rather than doing CPU work. It also auto-generates OpenAPI/Swagger documentation from type-hinted models, which made the API easy to test and hand off to the frontend without writing separate docs. Flask is sync by default and needs extensions for async; Django is heavier than needed for an API-only backend with no admin panel or templating requirements.

**Q: Is FastAPI a full framework like Django, or something else?**
A: It's a lightweight, API-focused framework — closer to Flask in philosophy than Django. It doesn't ship an ORM, admin panel, or templating engine; you bring your own (I used PyMongo directly rather than an ORM).

---

### Uvicorn
**Q: What does Uvicorn actually do, and why does FastAPI need it?**
A: FastAPI is an ASGI application — it defines how to handle requests, but it doesn't run a server on its own. Uvicorn is the ASGI server that actually listens on a port, accepts connections, and calls into the FastAPI app for each request. Without an ASGI server, FastAPI code has nothing to actually execute it.

**Q: What's the difference between WSGI and ASGI?**
A: WSGI (used by Flask/Django by default) is synchronous — one request per worker thread at a time. ASGI supports async natively, allowing a single worker to handle many concurrent requests while some are waiting on I/O, which is exactly the pattern this project needed for its external API calls.

---

### Pydantic
**Q: Why Pydantic models instead of raw dicts for request/response handling?**
A: Automatic validation — a malformed request gets rejected with a clear error before reaching business logic, instead of failing unpredictably deeper in the code. It also gives type safety during development and powers FastAPI's automatic OpenAPI documentation generation.

**Q: What happens if a request doesn't match the Pydantic schema?**
A: FastAPI automatically returns a 422 Unprocessable Entity response with details on which field failed validation — I didn't have to write that error-handling logic myself.

---

### LangChain
**Q: What exactly does LangChain provide in this project?**
A: The building blocks used *inside* each agent — prompt templates, the retriever interface over ChromaDB, the OpenAI LLM wrapper, and output parsing. It standardizes how these pieces connect so I wasn't writing raw API calls and manual prompt string formatting everywhere.

**Q: Could you have built this without LangChain, calling the OpenAI API directly?**
A: Yes, for a simpler version — but LangChain's retriever abstraction, prompt template management, and consistent interface across components saved a meaningful amount of boilerplate as the number of AI components grew.

---

### LangGraph
**Q: What does LangGraph add on top of LangChain?**
A: Orchestration — deciding *which* agents run for a given request and in what order, using a shared workflow state. LangChain provides the individual building blocks; LangGraph is the layer that wires them into a conditional workflow instead of a fixed sequential pipeline.

**Q: How does LangGraph decide the execution path for a request?**
A: Via conditional edges — a routing function inspects the current state (does this request have an image? a PDF? just text?) and returns which node should run next, instead of a fixed `add_edge` that always runs the same sequence.

---

### OpenAI Python SDK
**Q: Why use OpenAI's API instead of an open-source/self-hosted LLM?**
A: For a project at this scale, self-hosting a competitive LLM means managing GPU infrastructure, model serving, and quality tradeoffs that aren't worth it compared to a managed API with strong out-of-the-box quality, including multimodal (GPT-4V) support for the Vision component.

**Q: What are the downsides of relying on OpenAI's API specifically?**
A: Cost per call at scale, data leaving your infrastructure (a real concern for healthcare data — this is why PII redaction happens before anything is sent), and dependency on OpenAI's uptime and rate limits rather than something fully under your control.

---

### ChromaDB
**Q: Why ChromaDB over Pinecone, Weaviate, or FAISS?**
A: ChromaDB is lightweight and easy to run locally for a project at this scale, and integrates cleanly with LangChain's retriever abstraction. Pinecone/Weaviate are managed cloud services with added operational overhead and cost that isn't justified at this scale; FAISS is a lower-level library without Chroma's built-in persistence and metadata filtering.

**Q: What's actually stored in ChromaDB?**
A: Embedding vectors for each document chunk, plus associated metadata (source document, chunk index) that lets retrieved results be traced back to their origin.

---

### langchain_chroma / langchain_openai (integration layer)
**Q: What embedding model did you use, and why?**
A: OpenAI's `text-embedding-3-small` — a good cost/quality tradeoff for this scale, and keeping embeddings and generation on the same provider avoided extra integration overhead. For production, I'd benchmark it against domain-specific medical embedding models.

**Q: What's the actual role of these two packages versus LangChain core?**
A: They're provider-specific integration packages — `langchain_openai` wraps OpenAI's embedding and chat APIs into LangChain's standard interfaces, `langchain_chroma` does the same for ChromaDB. LangChain core defines the abstractions; these packages implement them for specific providers.

---

### Neo4j (Python driver)
**Q: Why a graph database when you already have RAG for retrieval?**
A: RAG retrieves documents but doesn't explicitly encode relationships. Neo4j lets the system directly traverse `Influenza → TREATED_BY → Paracetamol` instead of relying on a retrieved document to happen to state that clearly. They're complementary — RAG is content-first, the graph is relationship-first.

**Q: Why the raw driver instead of an ORM-style layer like `neomodel`?**
A: For a graph this size with targeted Cypher queries, writing Cypher directly is clearer and easier to optimize than translating through an object-graph mapper. I'd reconsider that if the schema grew significantly more complex.

---

### XGBoost
**Q: Why XGBoost over a neural network for symptom classification?**
A: The data is small and structured — binary symptom features mapped to disease labels. XGBoost handles structured tabular data like this efficiently, with built-in regularization to reduce overfitting, and doesn't need the volume of data or compute a neural network would to perform well.

**Q: What does XGBoost actually stand for and do at a high level?**
A: Extreme Gradient Boosting — it builds an ensemble of decision trees sequentially, where each new tree corrects the errors of the previous ones, combining many weak learners into a strong overall predictor.

---

### scikit-learn
**Q: What specifically did you use scikit-learn for, since XGBoost is a separate library?**
A: Train/test splitting (`train_test_split`) and evaluation metrics (`accuracy_score`, `precision_score`, `recall_score`, `f1_score`) — XGBoost provides the model itself, but scikit-learn provides the surrounding utilities for splitting data and measuring performance in a standard way.

**Q: Could scikit-learn's own classifiers have been used instead of XGBoost?**
A: Yes — Random Forest or Logistic Regression were considered alternatives, but XGBoost generally outperforms them on structured tabular data like this while still being fast to train.

---

### pandas / numpy
**Q: What role do pandas and numpy play specifically?**
A: pandas handles reading the CSV dataset, cleaning it, and structuring it into feature/label form for training and inference. numpy underlies pandas and XGBoost's numerical operations — most of my direct interaction was through pandas DataFrames rather than raw numpy arrays.

---

### joblib
**Q: Why joblib instead of Python's built-in pickle for saving the model?**
A: joblib is more efficient for objects with large internal NumPy arrays, which is what a fitted XGBoost model contains — it's also the convention scikit-learn's own documentation recommends for model persistence.

**Q: Why load the model once instead of on every request?**
A: Deserializing a model file is expensive relative to a single inference call. Loading it once at app startup and reusing the in-memory object avoids that repeated cost on every request.

---

### pytesseract (Tesseract)
**Q: Why Tesseract over a cloud OCR API like Google Cloud Vision?**
A: Tesseract is free, open-source, and runs locally without sending document images to a third party — relevant for healthcare documents. Google Cloud Vision offers better accuracy on lower-quality scans and was noted as an alternative for scaling, but for this project's scope Tesseract was sufficient and avoided extra API costs and data-sharing concerns.

**Q: What's a limitation of Tesseract you ran into or would expect?**
A: Accuracy drops noticeably on low-quality or skewed scans compared to cloud OCR services — a production version would likely need image preprocessing (deskewing, contrast enhancement) or a fallback to a cloud OCR provider for harder documents.

---

### re (regex, for PII redaction)
**Q: What's the actual limitation of using regex for PII detection?**
A: Regex works for structurally predictable fields — phone numbers, ID numbers with a fixed digit pattern — but patient names don't have a detectable pattern, so regex fundamentally can't catch those reliably.

**Q: What would you use instead for more robust PII detection?**
A: A Named Entity Recognition model — either spaCy's NER or a purpose-built tool like Microsoft's `presidio`, which is specifically designed for PII detection and handles unstructured fields like names that regex can't.

---

### PyMongo
**Q: Why MongoDB over a relational database like PostgreSQL for chat data?**
A: A conversation is naturally a nested document — a variable-length array of messages with evolving structure. MongoDB's document model fits that directly, whereas normalizing it across relational tables (a `conversations` table plus a separate `messages` table with foreign keys) adds complexity without much benefit for this access pattern.

**Q: What indexes would you add to the MongoDB collections?**
A: A compound index on `{userId: 1, updatedAt: -1}` on the conversations collection, since every history query filters by user and sorts by recency — that directly matches the actual query pattern.

---

### python-jose
**Q: Why JWT instead of server-side sessions?**
A: JWT is stateless — no session store to maintain, and every request carries the user's identity securely without server-side lookup. It also scales more naturally if the backend were split across multiple instances later, since there's no shared session state to synchronize.

**Q: What's actually inside the JWT payload?**
A: The user ID (`sub` claim) and an expiration timestamp (`exp`) — kept minimal deliberately, since anything in the payload is readable (though not modifiable without the secret key) by anyone who has the token.

---

### passlib (bcrypt)
**Q: Why bcrypt instead of a faster hash like SHA-256 for passwords?**
A: Speed is the wrong optimization target for password hashing — bcrypt is deliberately slow and includes a built-in salt, making brute-force and rainbow-table attacks impractical. A fast general-purpose hash is actually a bad choice for passwords for exactly that reason.

---

### React
**Q: Why React over Angular or Vue?**
A: Component-based architecture, a large ecosystem, and straightforward REST API integration were the main draws — React's learning curve and community support made it a practical choice for building the chat UI, upload flows, and history browser.

**Q: Where does React fit relative to the FastAPI backend?**
A: Purely as the presentation layer — it never talks to OpenAI, ChromaDB, or Neo4j directly. All of that goes through the FastAPI REST API, which keeps API keys and business logic off the client entirely.

---

### Axios
**Q: Why a service layer wrapping Axios instead of calling Axios directly in components?**
A: Centralizes API logic — if an endpoint shape changes, only the service function needs updating, not every component that calls it. It also lets me use an Axios interceptor to automatically attach the JWT to every outgoing request instead of manually adding auth headers everywhere.

---

### React Context API
**Q: Why Context API instead of Redux for state management?**
A: The app's state surface (user, JWT, active conversation, messages) is small enough that Redux's extra boilerplate — actions, reducers, store setup — wasn't justified. Context API is built into React and sufficient for state of this size; Redux becomes worth it at a scale of state complexity this project doesn't have yet.

---

### pytest
**Q: How do you test a LangGraph node in isolation using pytest?**
A: Each node is just a function that takes a state dict and returns a modified state dict, so it can be tested independently — feed it a mocked input state, call the node function directly (not the full compiled graph), and assert on the output state, without needing to run the whole pipeline or hit external APIs.
