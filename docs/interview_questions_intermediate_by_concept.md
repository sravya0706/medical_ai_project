# Intermediate Interview Questions — By Concept

General technical concepts, organized by domain. Not tied to any specific
project — these test understanding and tradeoffs, not recall of a
particular codebase. Answer style throughout: explain the concept, then
the *why* behind the tradeoff, not just a textbook definition.

---

## 1. Python & Software Engineering

**1. What's the difference between a shallow copy and a deep copy?**
A shallow copy creates a new outer object but still references the same nested objects inside it — mutating a nested list inside a shallow copy affects the original too. A deep copy recursively copies every nested object, so the two are fully independent. `copy.copy()` vs `copy.deepcopy()` in Python.

**2. Explain Python's GIL (Global Interpreter Lock) and why it matters for concurrency.**
The GIL ensures only one thread executes Python bytecode at a time, even on a multi-core machine. This means CPU-bound multithreading in Python doesn't get real parallelism — threads are still useful for I/O-bound work (waiting on network/disk), where the GIL is released during the wait. For genuine CPU-bound parallelism, you need multiprocessing (separate processes, separate GILs) instead.

**3. What's the difference between `@staticmethod` and `@classmethod`?**
A `@staticmethod` doesn't receive any implicit first argument — it's just a regular function namespaced inside a class. A `@classmethod` receives the class itself (`cls`) as its first argument, letting it access or modify class-level state, or serve as an alternative constructor (e.g., `from_json(cls, data)`).

**4. What's dependency injection, and why is it useful?**
Providing a component's dependencies from the outside rather than having it construct them itself — e.g., a function receiving a database connection as a parameter instead of creating one internally. This makes testing easier (swap in a mock), decouples components from specific implementations, and centralizes configuration in one place.

**5. What's the difference between unit tests, integration tests, and end-to-end tests?**
Unit tests check one function/class in isolation, usually with dependencies mocked. Integration tests check that multiple components work together correctly (e.g., a service actually talking to a real test database). End-to-end tests exercise the whole system as a user would, through the actual interface (API calls or UI). Unit tests are fast and numerous; e2e tests are slow, few, and catch what the others can't.

**6. What's a race condition, and how do you prevent one?**
A bug that occurs when the correctness of a program depends on the relative timing of concurrent operations — e.g., two requests reading, modifying, and writing the same value, where one write clobbers the other. Prevented via atomic operations (database-level atomic increments/pushes), locks, or by structuring the operation so a single atomic call does the whole read-modify-write.

**7. What's the difference between REST and RPC-style APIs?**
REST models the API around resources and standard HTTP verbs (GET/POST/PUT/DELETE mapping to CRUD operations on a noun, like `/users/123`). RPC-style APIs model the API around actions/functions being called remotely (`/getUserById`, `/createOrder`), closer to calling a function over the network. REST emphasizes resource state; RPC emphasizes explicit operations.

---

## 2. Databases (SQL & NoSQL)

**8. What's the difference between a primary key and a foreign key?**
A primary key uniquely identifies a row within its own table. A foreign key is a column (or set of columns) in one table that references the primary key of another table, establishing a relationship between them and enforcing referential integrity.

**9. Explain ACID properties.**
Atomicity — a transaction fully completes or fully rolls back, no partial state. Consistency — a transaction moves the database from one valid state to another, respecting constraints. Isolation — concurrent transactions don't interfere with each other's intermediate states. Durability — once committed, a transaction's changes survive a crash.

**10. What's database indexing, and what's the tradeoff of adding more indexes?**
An index lets the database find matching rows without scanning the whole table, dramatically speeding up reads matching that pattern. The tradeoff: every index adds overhead to writes (the index itself must be updated on every insert/update/delete) and consumes additional storage. Indexing is a read/write tradeoff, not a free performance win.

**11. What's a compound index, and when would you use one over two separate single-field indexes?**
An index spanning multiple fields together, ordered in a specific sequence. Useful when queries consistently filter and/or sort by the same combination of fields — a compound index on `(user_id, created_at)` can satisfy both "filter by user" and "sort by date" from one index, whereas two separate single-field indexes can't be combined as efficiently for that same query pattern.

**12. When would you choose a NoSQL document database over a relational database?**
When the data is naturally nested/hierarchical and doesn't fit cleanly into normalized tables (e.g., a chat conversation with a variable-length array of messages), when the schema needs to evolve frequently without migrations, or when horizontal scaling of writes matters more than complex multi-table joins and strict relational integrity.

**13. What's database normalization, and what's denormalization for?**
Normalization organizes data to minimize redundancy — splitting related data into separate tables connected by foreign keys, so a fact is stored in exactly one place. Denormalization intentionally duplicates data (or embeds related data together) to optimize for read performance, at the cost of needing to keep duplicated copies in sync on writes. Document databases often lean denormalized by design.

**14. What's a database transaction, and why might you need one across multiple operations?**
A group of operations that must all succeed or all fail together, treated as a single atomic unit. Needed when partial completion would leave the data in an inconsistent state — e.g., transferring money between two accounts: debiting one account but failing to credit the other would corrupt the data if not wrapped in a transaction.

**15. What's connection pooling, and why does it matter?**
Reusing a fixed set of already-open database connections across requests instead of opening and closing a new connection for every single query. Opening a connection has real overhead (TCP handshake, auth); pooling avoids paying that cost repeatedly and prevents a spike in requests from exhausting the database's max-connections limit.

---

## 3. API & Backend System Design

**16. What's the difference between authentication and authorization?**
Authentication answers "who are you" — verifying identity, typically via credentials or a token. Authorization answers "what are you allowed to do" — even after identity is confirmed, a separate check determines whether this specific user can access this specific resource or perform this specific action.

**17. What's idempotency, and why does it matter for API design?**
An idempotent operation produces the same end result no matter how many times it's called with the same input — calling it twice has the same effect as calling it once. Matters for retries: if a client doesn't know whether a request succeeded (e.g., after a timeout) and retries it, an idempotent endpoint won't create a duplicate side effect, while a non-idempotent one might.

**18. What's the difference between synchronous and asynchronous processing, and when would you use a message queue?**
Synchronous processing blocks the caller until the operation finishes. Asynchronous processing lets the caller continue without waiting, often via a queue — the request is accepted, queued, and processed separately, with the result delivered later (polling, webhook, or websocket). A message queue is useful when an operation is slow, can fail and needs retrying independently, or when you want to decouple the rate of incoming requests from the rate of processing.

**19. What's rate limiting, and what are common strategies for implementing it?**
Restricting how many requests a client can make in a given time window, to protect the service from abuse or overload. Common strategies: fixed window (simple, but allows bursts at window boundaries), sliding window (smoother, more accurate), and token bucket (allows controlled bursts while enforcing an average rate).

**20. What's the difference between horizontal and vertical scaling?**
Vertical scaling means making a single machine more powerful (more CPU/RAM). Horizontal scaling means adding more machines and distributing load across them. Vertical scaling has a hard ceiling and a single point of failure; horizontal scaling requires the application to be designed for it (typically meaning it needs to be stateless, or state needs to be externalized to a shared store).

**21. Why does a stateless API design matter for scaling?**
If a server doesn't hold any client-specific state between requests (e.g., session data lives in a token or external store, not server memory), any request can be routed to any server instance behind a load balancer. A stateful design would require "sticky sessions," pinning a client to one specific server — which undermines the whole point of having multiple interchangeable servers.

**22. What's CORS, and why does the browser enforce it?**
Cross-Origin Resource Sharing — a browser security mechanism restricting whether a webpage running on one origin (domain/port) can make requests to a different origin. It exists to prevent a malicious site from silently making authenticated requests to another site on a user's behalf using their existing cookies/session. The server must explicitly opt in via response headers (`Access-Control-Allow-Origin`, etc.) for cross-origin requests to succeed — and for many request types, the browser sends a preflight `OPTIONS` request first to check permission before sending the real request.

---

## 4. Machine Learning Fundamentals

**23. What's the difference between supervised, unsupervised, and reinforcement learning?**
Supervised learning trains on labeled input-output pairs to predict a label for new inputs. Unsupervised learning finds structure or patterns in unlabeled data (e.g., clustering). Reinforcement learning trains an agent to take actions in an environment to maximize cumulative reward, learning from consequences rather than labeled examples.

**24. Explain overfitting and underfitting.**
Overfitting: the model learns the training data too specifically, including its noise, and performs well on training data but poorly on new data — high variance. Underfitting: the model is too simple to capture the real pattern in the data, performing poorly on both training and new data — high bias. The goal is the balance point between the two.

**25. What's the bias-variance tradeoff?**
Bias is error from overly simplistic assumptions (the model can't capture the true pattern). Variance is error from being overly sensitive to the specific training data (the model captures noise as if it were signal). Reducing one often increases the other — model complexity is a dial between them, and the goal is minimizing total error, not either component alone.

**26. Explain precision, recall, and F1-score, and give a scenario where you'd prioritize one over the other.**
Precision: of everything predicted positive, how much was correct (minimizes false positives). Recall: of everything actually positive, how much was caught (minimizes false negatives). F1: harmonic mean of both. In fraud detection, you might prioritize recall (catch as much fraud as possible, tolerate some false alarms); in a spam filter, you might prioritize precision (don't want to lose real emails, tolerate some spam getting through).

**27. What's cross-validation, and why not just use a single train/test split?**
Cross-validation splits data into multiple folds, training and testing across different combinations and averaging the results, rather than relying on one fixed split. A single split's performance estimate can be skewed by which specific rows happened to land in the test set (especially with a smaller dataset) — cross-validation gives a more reliable, lower-variance estimate of how the model generalizes.

**28. What's regularization, and how does it help prevent overfitting?**
A technique that adds a penalty for model complexity (e.g., large weights) to the training objective, discouraging the model from fitting noise too closely. L1 regularization tends to push some weights to exactly zero (feature selection); L2 shrinks weights smoothly without necessarily zeroing them out.

**29. What's feature engineering, and why does it still matter even with modern models?**
Transforming raw data into features that better represent the underlying problem for a model to learn from — e.g., converting a timestamp into "hour of day" and "day of week" separately, which might be more predictive than the raw timestamp. Even with powerful models, better features often improve performance more than a more complex model on poorly-represented data — "garbage in, garbage out" still applies.

---

## 5. NLP & LLM Concepts

**30. What is a token, and how is tokenization different from just splitting on spaces?**
A token is a unit of text a model processes — often a sub-word piece, not a whole word. Tokenization uses a learned vocabulary (e.g., Byte-Pair Encoding) to split text into these pieces, which handles rare/unseen words gracefully by breaking them into familiar sub-word chunks rather than treating every distinct word as an entirely separate, unrelated symbol.

**31. What is an embedding, and why do semantically similar pieces of text end up numerically close together?**
A fixed-length vector representation of text, learned such that the geometric relationships between vectors reflect semantic relationships between the original text. This emerges from training the embedding model on massive amounts of text where similar contexts predict similar surrounding words/meaning — words or phrases used in similar contexts end up with similar vector representations.

**32. What's the difference between a transformer and earlier architectures like RNNs, at a conceptual level?**
RNNs process a sequence one token at a time, in order, carrying forward a hidden state — this makes them inherently sequential (slow to train, and long-range dependencies can fade over many steps). Transformers process the whole sequence at once using an attention mechanism, letting every token directly relate to every other token regardless of distance, which both parallelizes better and captures long-range relationships more effectively.

**33. What's the difference between fine-tuning and prompt engineering?**
Fine-tuning updates a model's weights using additional training data, changing its underlying behavior permanently. Prompt engineering shapes the model's output through the input alone, without touching the weights — same model, different instructions/examples/context. Fine-tuning is more powerful for consistent behavior change but expensive and slower to iterate on; prompt engineering is fast to iterate but bounded by what the base model can already do.

**34. What's hallucination in an LLM, and name two distinct mitigation strategies.**
When a model generates plausible-sounding but false or unsupported information. Mitigation strategies: (1) RAG — grounding the model's answer in retrieved, verifiable documents rather than relying on its internal parametric knowledge; (2) prompt constraints — explicitly instructing the model to only answer from provided context and to say "I don't know" rather than guess when context is insufficient.

**35. What's the difference between zero-shot, one-shot, and few-shot prompting?**
Zero-shot: asking the model to perform a task with no examples, just instructions. One-shot: providing exactly one example of the desired input/output pattern. Few-shot: providing several examples. More examples generally help the model better infer the exact format/style expected, at the cost of using more tokens in the prompt.

**36. What is temperature in LLM generation, and what does setting it near 0 actually do?**
A parameter controlling randomness in next-token sampling. Near 0, the model becomes close to deterministic, almost always picking the highest-probability token — useful when you want consistent, focused output (e.g., factual Q&A, code generation). Higher temperature flattens the probability distribution, allowing lower-probability tokens to be chosen more often, producing more varied/creative output.

---

## 6. RAG & Vector Databases

**37. Explain RAG (Retrieval-Augmented Generation) end to end, conceptually.**
Instead of asking an LLM to answer purely from what it learned during training, RAG first retrieves relevant documents from an external knowledge source (typically via semantic similarity search over embeddings), then includes those retrieved documents in the prompt as context, and asks the model to answer based on that context. This keeps answers grounded in verifiable, up-to-date, swappable knowledge rather than the model's frozen training data.

**38. What's the difference between a vector database and a traditional database, at the indexing level?**
Traditional databases use indexes like B-trees, optimized for exact-match or range queries on structured fields. Vector databases use specialized indexes (like HNSW — Hierarchical Navigable Small World graphs) optimized for approximate nearest-neighbor search over high-dimensional vectors — finding "the most similar" rather than "the exact match."

**39. Why "approximate" nearest neighbor search instead of exact?**
Exact nearest-neighbor search in high-dimensional space requires comparing a query against every single vector, which doesn't scale to large collections. Approximate methods trade a small amount of accuracy for massive speed gains by using graph or tree structures that narrow the search space intelligently, without guaranteeing the mathematically closest match every time — in practice, close enough for most retrieval use cases.

**40. What's chunking, and why does chunk size matter?**
Splitting long documents into smaller pieces before embedding and storing them, since embedding models have limited input length and retrieval works better on focused units of meaning rather than whole documents. Too small, and chunks lose surrounding context; too large, and irrelevant content gets pulled in alongside what's actually relevant, diluting retrieval precision and wasting tokens.

**41. What's chunk overlap, and why include it?**
Including a small amount of shared text between consecutive chunks, so information near a chunk boundary isn't split awkwardly across two chunks with neither containing the full relevant context. The tradeoff is some redundant storage and slightly more tokens indexed overall.

**42. What's the difference between top-k retrieval and similarity-threshold retrieval?**
Top-k always returns a fixed number of results, regardless of how relevant they actually are — even weak matches get returned to fill the quota if nothing better exists. Threshold-based retrieval only returns results above a minimum similarity score, which can return fewer (or zero) results but avoids including irrelevant content just to hit a count.

---

## 7. Agent Orchestration & LangChain/LangGraph

**43. What problem does an orchestration framework like LangGraph solve that a simple sequential pipeline doesn't?**
A sequential pipeline runs every step in the same fixed order for every request, regardless of whether that step is actually needed — wasteful once you have multiple distinct processing paths (e.g., text vs. image input needing different handling). An orchestration framework allows conditional routing — only the nodes relevant to a given request's type actually execute — plus shared state management across whichever nodes do run.

**44. What's the conceptual difference between LangChain and LangGraph?**
LangChain provides individual building blocks — prompt templates, retrievers, LLM wrappers, output parsers — the components used *inside* one processing step. LangGraph is a layer on top that decides which steps (each potentially built with LangChain components) execute, in what order, and how they share state — the orchestration logic connecting the building blocks together into a workflow.

**45. What's an "agent" in the LLM context, as distinct from a single prompt-response call?**
An agent typically refers to a system where the LLM (or a broader pipeline) can take multiple steps, potentially call external tools, make decisions about what to do next based on intermediate results, and iterate — as opposed to a single fixed prompt producing a single fixed response. The "agentic" quality is in the decision-making and multi-step execution, not just generating text once.

**46. Why might you keep some routing/safety logic deterministic and rule-based rather than letting an LLM decide?**
For high-stakes or safety-critical decisions, deterministic rule-based logic is predictable, auditable, and testable in a way that relies on exact, verifiable behavior every time. An LLM-based decision, even a well-prompted one, carries some irreducible uncertainty about its exact output. For cases where you need a guarantee (e.g., detecting an emergency), a rule-based check that's fast and 100% predictable is often preferable to routing that decision through a model, even if the model would usually get it right.

---

## 8. Security

**47. Why is bcrypt (or similar) used for password hashing instead of a fast hash like SHA-256?**
Password hashing needs to be deliberately slow to make brute-force attacks impractical — trying billions of guesses per second is the attacker's goal, and a fast hash like SHA-256 makes that easy. bcrypt (and similar algorithms like Argon2) are intentionally computationally expensive and include a built-in salt, which also defeats precomputed rainbow-table attacks.

**48. What's a JWT, and what does "signed but not encrypted" mean in practice?**
A JSON Web Token — a compact, self-contained token typically carrying claims (like a user ID and expiry) as its payload. It's signed with a secret key, meaning the server can verify it hasn't been tampered with, but the payload itself is only base64-encoded, not encrypted — anyone who has the token can read its contents, they just can't forge a valid new one without the secret key. This means sensitive data should never go in a JWT payload.

**49. What's the principle of least privilege, and how does it apply to API design?**
Granting only the minimum access necessary to perform a task, nothing more. In API design, this shows up as authorization checks scoped as narrowly as possible — a user's token should only grant access to their own resources, not broad access "just in case," and different roles should have explicitly different permission sets rather than one broad set everyone shares.

**50. What's the difference between input validation and sanitization?**
Validation checks that input conforms to expected rules (correct type, format, length) and rejects it outright if it doesn't. Sanitization modifies input to make it safe (e.g., escaping special characters) rather than rejecting it. Both matter, but for security-sensitive contexts, rejecting invalid input outright is often safer than trying to "fix" it, since sanitization logic itself can have gaps an attacker exploits.
