# MediAssist — Intermediate Interview Questions (Project-Specific)

Project-specific, intermediate tier — sits between Basic ("what did you
build") and Advanced ("how would you scale/fail-mode this"). These probe
*how* things actually work: real library choices, real code-level
decisions, and the reasoning behind specific implementation details.

---

## Architecture & Design Decisions

**1. Walk me through the exact request lifecycle for a text message, file by file.**
`ChatPage.jsx` calls `chatService.js`, which posts through the Axios instance in `api.js` (JWT auto-attached via interceptor) to `POST /api/v1/chat`. `chat_routes.py` validates the JWT via `auth/dependencies.py`, then calls `agents/orchestrator.py::run_pipeline()`. That runs the LangGraph state machine — guardrail check, NLP extraction, classification, RAG retrieval, KG enrichment, memory lookup, prompt building, and the OpenAI call — then returns a result dict. The route persists the exchange to MongoDB (reusing one conversation per session) and returns a `ChatResponse` back to the frontend, which renders it as a `MessageBubble`.

**2. Why does the guardrail check happen before NLP/RAG/classification instead of after, like the original architecture describes?**
If a message is going to be overridden with a fixed escalation response regardless of what downstream processing would produce, running that processing first just wastes compute and API cost. Checking guardrails as the very first LangGraph node means an emergency message short-circuits straight to the response with the lowest possible latency — a deliberate efficiency choice, not an oversight.

**3. Your workflow state has both an `error` field and a `vision_error` field. Why two separate fields instead of one?**
They have different failure semantics. `vision_error` is non-fatal — if the Vision LLM call fails, the pipeline continues with the text-only query, since a failed image analysis shouldn't block an otherwise-answerable text request. `error` is fatal — it's checked explicitly in `run_pipeline()` to short-circuit and return a 503, because a failed final-generation call means there's genuinely no response to give.

**4. Why is the LangGraph compiled once and cached at module level instead of rebuilt on every request?**
Compiling a `StateGraph` has real overhead — building the node/edge structure isn't free. Since the graph's structure never changes at runtime, it's built once on first use (`get_graph()` checks a module-level `_compiled_graph` global) and reused for every subsequent request, the same caching pattern used for the XGBoost model in `ml/predict.py`.

**5. Why is Controller/Service/Repository separation useful here specifically, beyond "it's a best practice"?**
Concretely: `chat_routes.py` (controller-ish layer) never touches MongoDB directly — it calls functions from `db/mongo_client.py` (repository layer). If I swapped MongoDB for PostgreSQL, only `mongo_client.py` would need to change; the route logic, the orchestrator, and the frontend would all be completely unaffected. That's the actual payoff, not just a theoretical one.

---

## NLP & Symptom Classification

**6. Your NLP extractor is keyword/phrase matching, not a trained model. What's the actual mechanism, and what breaks it?**
`SYMPTOM_LEXICON` maps each symptom key to a list of trigger phrases (`"fever"` → `["fever", "high temperature", "burning up"]`). The extractor scans the lowercased input text for any matching phrase. What breaks it: anything phrased outside the lexicon — "I've been running hot" wouldn't match "fever" at all, since there's no semantic understanding, only literal substring matching.

**7. Why binary flags (`{"fever": 1, "cough": 1}`) instead of, say, a severity score per symptom?**
That's the exact input shape the XGBoost classifier was trained on — the dataset itself is binary symptom presence/absence per disease. Changing to a severity score would require retraining on a dataset that actually captures severity, which the synthetic dataset doesn't model.

**8. Walk me through what happens if the classifier receives an empty symptom dict.**
`classify_node` checks `if symptoms:` before calling `predict_conditions()` — if the NLP step extracted nothing, it skips classification entirely and sets `predicted_conditions` to an empty list, rather than calling the model with an all-zero feature vector (which would produce a meaningless prediction dressed up as a real one).

**9. Your `train.py` uses `stratify=y` in the train/test split. What does that do and why does it matter here?**
It ensures each class (disease) is proportionally represented in both the train and test sets, matching its proportion in the full dataset. Without it, a random split could accidentally under-represent a disease in the test set, making that disease's evaluation metrics unreliable due to too few examples — especially relevant with 10 classes and a moderate dataset size.

**10. Why `joblib.dump()` for three separate artifacts (model, label encoder, column list) instead of one combined object?**
Each has a distinct lifecycle concern: the model does inference, the label encoder translates between the model's integer output and human-readable disease names, and the column list ensures a feature dict at inference time gets mapped to the exact same column order used during training — mismatched column order would silently produce wrong predictions without erroring. Keeping them separate makes each easy to version or swap independently if needed.

---

## RAG Pipeline

**11. Your embedding function is TF-IDF, fit once during ingestion. What breaks if you fit it again during retrieval instead of loading the saved one?**
TF-IDF vectors are only meaningful relative to the vocabulary they were fit on. If you re-fit on a single query at retrieval time, the resulting vector space would only contain that query's words — completely incompatible with the vectors already stored in ChromaDB from ingestion. The embedding function must `.load()` the persisted vectorizer, not `.fit()` a new one, or every similarity comparison becomes meaningless.

**12. Your `TfidfEmbeddingFunction` subclasses ChromaDB's `EmbeddingFunction` protocol. What methods does that actually require, and why?**
At minimum `__call__()` (turns text into vectors) — but the ChromaDB version used also required `name()`, `get_config()`, and `build_from_config()` for the collection's internal validation/persistence logic. Missing these caused an `AttributeError` during development until they were added — a good example of an interface contract not being obvious from just implementing the "main" method.

**13. Why does `retrieve()` return an empty list instead of raising an exception when the collection is empty?**
So the caller — ultimately `prompt_builder.py` — can distinguish "nothing was retrieved" as a valid state to build a prompt around ("No relevant medical documents were retrieved"), rather than the request failing outright. This is the actual hallucination-mitigation mechanism at work: even a retrieval miss produces an honest, gracefully-handled prompt rather than an error or a silent fallback to ungrounded generation.

**14. What's the actual chunking configuration, and why those specific numbers?**
500-character chunks with 100-character overlap, via `RecursiveCharacterTextSplitter`, which tries splitting on paragraph breaks first, then sentences, before falling back to a hard character cut — preserving semantic coherence better than a naive fixed-width split. The specific numbers were a documented balance point: smaller fragmented context, larger increased token cost without proportional benefit.

---

## Knowledge Graph

**15. Walk me through exactly what happens, step by step, when `get_related_entities()` is called and Neo4j is unreachable.**
`get_driver()` returns a driver instance (lazily created, doesn't fail yet). The `with driver.session()` block attempts to actually connect and run the Cypher query, which raises `ServiceUnavailable`. That specific exception is caught (not a broad `except Exception` at that point), logged with a clear message, and the function returns the same empty-but-valid structure (`{"available": False, ...}`) it would return if the disease simply wasn't in the graph — same code path for two different root causes, both handled the same documented way.

**16. Why catch `ServiceUnavailable` and `AuthError` specifically, with a separate broader `except Exception` after?**
The specific exceptions represent expected, anticipated failure modes (no server running, wrong credentials) that should degrade gracefully and quietly. The broader catch-all is a safety net for genuinely unexpected errors, which still get logged and still degrade gracefully — but distinguishing them in the log message helps debugging later (an "unexpected" error is a signal something is actually wrong, versus an expected/normal offline state).

**17. Your Cypher seed script uses `MERGE` instead of `CREATE`. What's the practical consequence of getting that wrong?**
`CREATE` always creates a new node/relationship, even if an identical one already exists — running the seed script twice with `CREATE` would produce duplicate `Influenza` nodes, breaking every downstream query that expects exactly one match per disease name. `MERGE` checks for an existing match first and only creates if none exists, making the script safely re-runnable.

---

## Vision & Orchestration

**18. How do vision findings actually get incorporated into the rest of the pipeline — is there a separate "vision" data path?**
No — `vision_node` merges the findings text directly into `state["query"]` itself (`f"{query}\n\n[Image findings: {findings}]"`), so every downstream node (NLP extraction, RAG retrieval) operates on the combined text exactly as if the user had typed the findings themselves. There's no separate vision-specific code path threaded through the rest of the graph — this was a deliberate simplification, and it matches the documented principle that Vision only produces findings, never answers directly.

**19. Why does image routing happen via `add_conditional_edges` rather than a simple `if image_b64: run_vision()` check inside a single node?**
Because LangGraph's conditional edges are what make a node's execution actually optional at the graph level — `vision_node` genuinely doesn't run at all for text-only requests, rather than running and immediately no-opping. It's a real architectural distinction: conditional routing skips work entirely; an in-node `if` check would still pay the cost of entering that function on every request.

**20. What validation happens before an uploaded image ever reaches the Vision LLM call?**
`upload_validation.py::validate_and_encode_image()` checks the declared `content_type` against an allowlist (`image/png`, `image/jpeg`) and the file size against `settings.max_upload_mb`, raising a 400 before any of that data reaches the LangGraph pipeline at all. Bad uploads get rejected at the edge, not deep inside the AI processing.

---

## Prompt Building & LLM Integration

**21. What exactly goes into the final prompt sent to OpenAI — walk through the actual structure.**
Two messages: a fixed `system` message (the hallucination-mitigation instructions — answer only from context, admit insufficient information, never give a definitive diagnosis) and a `user` message assembled from four labeled sections: conversation history, retrieved RAG context, the classifier's predicted conditions with confidence percentages, and any knowledge graph relationships — followed by the actual current question.

**22. Why does `get_client()` raise an exception instead of returning a mock/fake response when `OPENAI_API_KEY` isn't set?**
Because a fabricated response that looks like a real model output would be actively misleading — anyone testing against it could mistake fake output for a working integration. Raising `LLMNotConfiguredError` immediately makes the missing configuration impossible to miss, and it's turned into a clear 503 at the route level rather than silently degrading into fake data.

**23. Your temperature is set to 0.3. What's the actual reasoning, and what would change if you set it to 0.9?**
Lower temperature (0.3) biases toward the model's most probable next token, producing more consistent, focused output — appropriate for a domain where the same symptom description should generally get similar grounded guidance across repeated asks. At 0.9, output would become noticeably more varied and creative, which is a liability here, not a feature — you don't want a medical assistant answering the identical question differently depending on random sampling.

---

## Auth, Persistence & Memory

**24. Why does `create_access_token()` only put the user ID in the JWT payload, not the email or any other user data?**
Anything in a JWT payload is readable by anyone holding the token — it's signed, not encrypted. Keeping the payload minimal (just `sub` and `exp`) means there's nothing sensitive exposed if a token were intercepted, beyond "this identifies some user ID." Anything else needed (like email) gets looked up fresh from the database using that ID, rather than trusted from the token itself.

**25. Walk me through the actual bug that existed before `conversation_map.py`, and why it wasn't obvious until the frontend was built.**
Originally, `chat_routes.py` called `create_conversation()` unconditionally on every single chat message, meaning every message became its own brand-new "conversation" in MongoDB. This was invisible while testing purely via curl/Swagger, since nothing was rendering the history list — it only became obviously broken once the Sidebar component started displaying "conversations" and every single one contained exactly one message. The fix maps `session_id → conversation_id` so a session's messages append to one growing thread.

**26. Why is `is_mongo_available()` checked before every Mongo-dependent operation, rather than just letting the operation fail naturally and catching the exception?**
Partly for fast, clear error messages (checking a ping is fast and lets the route return a specific "MongoDB is not reachable" 503 immediately, versus a generic exception surfacing from deep inside a query). It's also used in `chat_routes.py` to decide whether to *attempt* persistence at all — a chat response should still return successfully to the user even if Mongo is down, and checking availability upfront makes that branch explicit in the code rather than relying on exception handling to fall through gracefully.

**27. What's the actual difference in the code between Conversation Memory and Chat History persistence?**
`memory/session_memory.py` is a plain Python dict, updated via `add_turn()`, read via `get_recent_history_text()` — pure in-process state with no database involved. `db/mongo_client.py`'s `append_message()` writes to an actual MongoDB document via an atomic `$push`. They're triggered by the same events (a message being sent/received) but serve completely different purposes — one feeds the next prompt's context, the other is what the History sidebar reads from.

---

## Frontend Integration

**28. How does the frontend know a user's session without a backend `/me` endpoint returning user details?**
It decodes the JWT payload client-side (`JSON.parse(atob(token.split(".")[1]))`) purely for display purposes — pulling out the `sub` claim to show *something* identifying in the Sidebar footer. This is explicitly not a security check (the frontend never verifies the signature — it doesn't have the secret key to) — it's just reading data that's already readable by design, for a cosmetic label.

**29. Why does `ChatPage.jsx` funnel both `handleSend` and `handleSendImage` through one shared `runExchange()` function?**
Because the state transitions are identical regardless of message type — append the user's message optimistically, show the loading indicator, call some API function, append the response or show an error, refresh the conversation list. The only actual difference is which API function gets called, so that's the one thing passed in as a parameter, avoiding duplicating the whole send/receive/error flow for two nearly-identical cases.

**30. What actually happens in the browser when a request gets a 401 back?**
An Axios response interceptor in `api.js` checks every response for a 401 status; if found, it clears the JWT from `localStorage` and hard-redirects to `/login` — centrally, in one place, rather than every component that makes an API call needing its own "did my session expire" handling.

---

## Testing & Verification (what was actually checked, not just claimed)

**31. How did you actually verify the LangGraph orchestrator worked correctly, beyond "I wrote the code"?**
Ran it directly via its own `if __name__ == "__main__"` block with three cases: a high-risk message (confirmed it short-circuited to escalation with zero downstream calls), a normal symptom message (confirmed it flowed through every node and correctly failed at the final LLM call with a clear config error, not a crash), and an image-path message with no vision API access (confirmed `vision_error` was set and the pipeline still continued through the rest of the graph rather than aborting).

**32. What was the actual proof that CORS was fixed, not just "I added the middleware"?**
Sent a real `curl -X OPTIONS` request with `Origin` and `Access-Control-Request-Method` headers set — the same shape of request a browser sends as a preflight — and confirmed the response changed from a 405 to a 200 with the correct `access-control-allow-origin` header present, rather than just trusting that adding `CORSMiddleware` was sufficient.
