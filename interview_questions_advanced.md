# MediAssist — Advanced Interview Questions

Project-specific, advanced tier. These probe tradeoffs, failure modes, scaling, and "what would you do differently" — the questions that separate someone who built a demo from someone who understands the system deeply enough to defend and evolve it.

---

## Architecture & System Design

**1. Your architecture has a lot of moving pieces — NLP, classifier, RAG, KG, Vision, OCR, memory. How would you decide what to cut if you had to ship an MVP in half the time?**
I'd keep NLP → RAG → Prompt Builder → GPT as the non-negotiable core, since that's what actually grounds responses and prevents hallucination. Vision and OCR are additive input modalities — valuable but not core to the safety story. The Knowledge Graph is the first thing I'd cut under real time pressure, since RAG alone still produces reasonable answers without it; the graph is an enrichment layer, not a dependency, which is exactly how I built it to degrade.

**2. Walk me through what happens end-to-end if ChromaDB is down when a request comes in.**
The RAG retrieval step would fail or return empty. I'd want a fallback where the Prompt Builder detects zero retrieved documents and explicitly tells GPT to state it lacks grounded information rather than silently falling back to ungrounded generation — that's actually the same code path as a "no relevant results" case, just triggered by an outage instead of a genuine gap in the knowledge base. In a production version I'd also want a circuit breaker so we're not retrying a dead service on every request and adding latency.

**3. How would you scale this to handle 10,000 concurrent users?**
A few layers: put the FastAPI backend behind a load balancer with multiple stateless instances (JWT already makes this easy since there's no server-side session state to share); move Conversation Memory to Redis instead of in-process so any instance can serve any user; add a queue for expensive operations like OCR and Vision LLM calls so they don't block the request thread; and cache frequent RAG queries. The database layer — MongoDB, ChromaDB, Neo4j — would each need their own scaling story (MongoDB replication/sharding, Chroma or a managed vector DB with horizontal scaling, Neo4j read replicas).

**4. Why a monolithic FastAPI backend instead of microservices from the start?**
For a project at this stage, a monolith was faster to build, easier to debug, and avoided premature distributed-systems complexity — network calls between services, service discovery, distributed tracing — none of which pays off until you actually have independent scaling or deployment needs. The layered structure (Controller/Service/Repository) means the boundaries for a future microservices split — e.g., pulling out the Vision/OCR pipeline as its own service — are already there if I needed them.

**5. If you were rebuilding this today, what would you change architecturally?**
I'd seriously consider replacing the fixed multi-agent LangGraph structure with a more dynamic agent that can decide its own tool calls, rather than hand-coding routing logic — trading some predictability for flexibility as new capabilities get added. I'd also push PII redaction and safety guardrails earlier and make them independently testable modules rather than steps embedded in the pipeline, so they could be unit-tested and audited in isolation — that matters more the closer you get to a real compliance conversation.

---

## RAG & Retrieval

**6. Your chunk size is fixed at roughly 500 tokens with 100 overlap. When would fixed-size chunking break down, and what would you use instead?**
Fixed-size chunking ignores document structure — it can split a symptom list or a dosage instruction mid-sentence. For this project's scale it was good enough, but a more robust approach would be semantic or structure-aware chunking — splitting on section headers or using an embedding-based method to detect topic boundaries — so a chunk is a coherent unit of medical meaning rather than an arbitrary token window.

**7. How would you detect and prevent retrieval drift over time as your medical knowledge base grows?**
I'd track retrieval precision against a fixed evaluation set on every knowledge base update — not just when I first tune it — so I can catch degradation from noisy or overlapping documents being added. I'd also want per-query logging of what got retrieved vs. what the response actually used, so I can spot cases where retrieval quality silently drops even though the final answer still looks fine.

**8. What's the failure mode where RAG retrieves *technically relevant but medically wrong* documents, and how would you guard against it?**
This is the scariest failure mode in a medical RAG system — confidently grounded, wrong. Mitigations: source curation (only ingest from vetted medical references, not arbitrary web content), a re-ranking step after initial retrieval that scores relevance more strictly than embedding similarity alone, and keeping the Knowledge Graph as a second, structurally independent source of truth that can catch a contradiction — if RAG says one thing and the graph relationship says another, that's a signal to hedge the answer rather than commit to it.

**9. How would you handle multi-hop questions that RAG alone struggles with — e.g., "what should I avoid if I'm already on blood thinners and now have a fever"?**
That's exactly the case for combining RAG with the Knowledge Graph's multi-hop traversal — RAG retrieves general fever guidance, but the graph can explicitly traverse medication-interaction relationships if I extend the schema to include drug-interaction edges. Right now my graph doesn't model drug interactions, which I'd flag as a real gap if asked directly — it's a good example of scope I consciously left out of a personal project.

---

## Classifier & ML

**10. Your XGBoost classifier hits 85%+ on a Kaggle dataset. Why might that number be misleading in a real clinical setting?**
Kaggle symptom-disease datasets tend to be cleaner and more separable than real patient-reported symptoms, which are noisy, incomplete, and often described in inconsistent language even after NLP extraction. Real-world accuracy would likely be lower due to distribution shift — the model has never seen the messiness of how actual users phrase and combine symptoms. I'd be upfront that 85% is a benchmark on a curated dataset, not a claim about real-world clinical accuracy.

**11. How would you detect if the classifier's predictions are silently degrading after deployment?**
I'd track prediction confidence distributions over time and flag drift, plus periodically sample predictions for manual review against outcomes if that data were available. Without a feedback loop from actual outcomes, a classifier can degrade silently as the input distribution shifts and you'd have no signal — that's a real limitation of the current design that I'd want to close in a production version.

**12. Why not fine-tune the LLM itself on medical data instead of relying on RAG?**
Fine-tuning bakes knowledge into weights that go stale the moment guidelines update, and it's expensive to retrain every time. RAG keeps the knowledge base separately updatable — I can add a new medical document and it's immediately available to the system without touching the model at all. Fine-tuning also doesn't give you the same auditability; with RAG, I can point to exactly which document justified a given answer, which matters a lot in a healthcare context.

---

## Knowledge Graph

**13. How would you keep the Neo4j graph and the RAG document store from drifting out of sync as both get updated independently?**
Ideally, an ingestion pipeline treats them as one update event, not two — when a new medical document is added to the RAG store, an entity-extraction step also proposes new nodes/relationships for the graph, even if some go through manual review before being committed. Right now that sync isn't automated end-to-end in my implementation; it's a manual step, which I'd flag as the natural next piece of engineering work.

**14. When would GraphRAG-style traversal actually outperform your current two-step RAG-then-KG-enrichment approach?**
When the question genuinely requires multi-hop reasoning across many connected entities before an answer makes sense at all — e.g., "which conditions share three or more symptoms with mine and require the same specialist." My current design retrieves RAG content and separately enriches with one or two graph hops; a true GraphRAG approach would let the traversal itself drive what gets retrieved, which is a deeper architectural change, not just an enrichment step.

---

## Orchestration & Multi-Agent

**15. LangGraph gives you conditional routing, but how do you prevent the routing logic itself from becoming an unmaintainable pile of conditionals as you add more request types?**
By keeping routing rules declarative and centralized in one Request Analyzer / router module rather than scattering `if image / if pdf` checks across services — which is literally the problem LangGraph was introduced to solve in the first place, replacing ad hoc conditionals in the original sequential pipeline. If routing complexity kept growing, I'd consider a more general classifier-based router instead of hand-written rules — essentially using a lightweight model to decide the execution path instead of pattern-matching request types.

**16. What's your strategy for testing a LangGraph workflow — how do you know a routing change didn't silently break an existing path?**
Each node needs to be independently testable with mocked upstream state — I can feed a workflow state object into just the RAG node, for instance, and check its output without running the whole graph. For routing itself, I'd want a table of representative requests (text-only, image, PDF, follow-up) mapped to their expected execution path, run as a regression suite whenever routing logic changes — I don't currently have that formalized, which is an honest gap for a personal project versus something production-grade.

**17. How would you add cost controls so the system doesn't run away with OpenAI API spend under high load?**
Rate limiting per user, caching identical or near-identical queries, using a cheaper/faster model for the safety-guardrail severity check versus the final generation step, and setting hard per-session token budgets that trigger conversation summarization instead of sending ever-growing history on every call.

---

## Safety, Security & Compliance

**18. Your safety guardrail is rule-based and keyword/pattern driven. What happens when a user describes an emergency in a way your rules don't catch?**
That's the core weakness of a purely rule-based guardrail — recall depends entirely on how comprehensive the pattern list is, and natural language is endlessly variable. A more robust version would combine the rule-based check (which is fast, deterministic, and auditable) with an LLM-based secondary classifier trained or prompted specifically to flag ambiguous high-risk language, then take the more cautious of the two verdicts. I'd rather over-escalate a borderline case than under-escalate a real one.

**19. If this were a real product, what would you need to add for HIPAA-style compliance that isn't in your current design?**
Encryption at rest for MongoDB and file storage (not just HTTPS in transit), detailed audit logging of every access to patient data with who/when/what, formal data retention and deletion policies, business associate agreements if using third-party APIs like OpenAI with PHI, and likely a more rigorous PII redaction pipeline than pattern-matching — probably a dedicated NER model trained for PHI detection rather than regex-style rules, since regex will miss non-standard formats.

**20. Your PII redaction happens before embedding. How would you handle a case where PII leaks into the LLM's generated response itself, even if the input was clean?**
That's a distinct failure mode from input-side leakage — the model could still reconstruct or reference something PII-adjacent from context, even without literal training data leakage, especially if conversation history contains anything unredacted from earlier turns. I'd want an output-side scan as well — not just input-side — checking the generated response for PII patterns before it's returned, functioning as a second guardrail layer symmetric to the input redaction step.

---

## Evaluation & Reliability

**21. Manual evaluation of 100+ queries doesn't scale as a regression suite. How would you automate hallucination detection?**
An LLM-as-judge approach: feed the judge model the retrieved context and the generated response, and ask it to score whether every claim in the response is supported by the context — essentially automating what I did manually. I'd validate that judge against my manually-labeled 100 queries first to make sure it agrees with human judgment before trusting it to run unsupervised on every prompt or retrieval change going forward.

**22. How would you set up A/B testing between two prompt versions in a system this safety-sensitive?**
Carefully, and not with live medical guidance as the test surface without guardrails around it. I'd run both prompt versions against the same fixed evaluation set offline first, and only consider live traffic testing on a small percentage with the guardrail layer treated as identical and non-negotiable across both variants — the guardrails shouldn't be part of what's being tested.

**23. What's a metric you're NOT currently tracking that you think you should be?**
Time-to-escalation for high-risk cases — how many turns does it take before the guardrail triggers for a genuinely serious case? Right now I evaluate whether the guardrail triggers at all, but not how quickly, and in a real emergency, latency in escalation matters as much as eventual correctness.

---

## Closing "Systems Thinking" Question

**24. If you had one more month to work on this project, what's the single highest-leverage thing you'd build?**
An automated evaluation pipeline — turning my manual 100-query hallucination check into something that runs on every prompt or retrieval change and reports groundedness/relevance/retrieval-precision automatically. Right now improving the system means manually re-running my eyes over 100 responses, which doesn't scale and makes me less confident that a change I think is an improvement actually is one.
