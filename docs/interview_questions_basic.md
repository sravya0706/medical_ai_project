# MediAssist — Basic Interview Questions

Project-specific, basic tier only. These are the "can you explain what you built" questions — expect these first in almost any interview, from HR screens through technical rounds.

---

## Project Overview

**1. What is MediAssist and what problem does it solve?**
It's an AI-powered healthcare assistant that lets patients describe symptoms, upload prescriptions or medical images, and get grounded, safety-checked guidance in a conversational format — instead of a raw ChatGPT answer with no medical grounding or safety checks.

**2. What was the core technical challenge?**
Preventing hallucinated medical advice. An LLM alone can sound confident and still be wrong, which is dangerous in healthcare. The architecture is built around *grounding* — RAG, a knowledge graph, a classifier, and rule-based safety guardrails — rather than trusting the LLM's raw output.

**3. Walk me through the tech stack.**
FastAPI backend, React frontend, OpenAI ChatGPT API for generation, LangChain/LangGraph for orchestration, ChromaDB for vector search, Neo4j for the knowledge graph, MongoDB for app data, XGBoost for symptom classification, JWT for auth.

**4. Why did you build this project?**
To move from generalist full-stack/DevOps work into applied AI engineering — specifically to get hands-on with RAG, agent orchestration, and production-grade LLM system design rather than just calling an API.

---

## NLP & Symptom Classification

**5. What does the NLP layer actually do?**
Converts free text like "I've had a fever and cough for three days" into structured data — extracted symptoms and duration — that downstream components (classifier, RAG) can consume. It doesn't predict anything; it's pure extraction.

**6. What's the difference between NLP and the Symptom Classifier?**
NLP answers "what did the user say." The classifier answers "given those symptoms, what conditions are likely." One extracts, the other predicts.

**7. Which model did you use for classification and why?**
XGBoost, trained on a public Kaggle symptom-disease dataset. Chosen over deep learning because the data is small and structured (binary symptom features), where XGBoost outperforms a neural net with far less complexity and no GPU need.

**8. How did you get to 85% accuracy — and 85% of what, exactly?**
It's test-set accuracy, not training accuracy. I split the dataset 80/20, trained XGBoost on the 80%, and evaluated purely on the held-out 20% using accuracy, precision, recall, and F1. The final model scored above 85% on that unseen portion.

---

## RAG Pipeline

**9. Why RAG instead of just prompting GPT directly?**
Direct prompting relies on the model's internal, sometimes outdated or wrong, training knowledge. RAG retrieves actual medical documents first and constrains the prompt to answer only from that retrieved context — this is the core hallucination-reduction mechanism.

**10. What vector database did you use and why?**
ChromaDB — lightweight, easy to run locally for a project of this scale, and integrates cleanly with LangChain's retriever abstraction.

**11. What happens if RAG retrieves nothing relevant?**
The system prompt explicitly instructs the model to say it doesn't have enough information rather than answering from general knowledge.

---

## Knowledge Graph

**12. You already had RAG — why add a Knowledge Graph too?**
RAG retrieves documents but doesn't explicitly encode relationships. If a user asks "what treats influenza," RAG might return a document *about* influenza without a clean answer. Neo4j lets me directly traverse `Influenza → TREATED_BY → Paracetamol` — RAG is content-first, the graph is relationship-first. They complement each other.

**13. Why Neo4j specifically?**
It's a graph-native database optimized for relationship traversal via Cypher, which is exactly the query pattern needed here (symptom → disease → medication → specialist).

**14. What entities and relationships does your graph model?**
Nodes: Symptom, Disease, Medication, Treatment, Specialist. Relationships: HAS_SYMPTOM, TREATED_BY, REQUIRES_SPECIALIST, RELATED_TO, PREVENTED_BY.

---

## Vision LLM & OCR

**15. Why add image understanding to a text chatbot?**
Patients often want to show something — a rash, a prescription, a lab report — not just describe it in words. Ignoring that visual information meant losing real diagnostic-relevant context.

**16. Does the Vision LLM diagnose the image?**
No — deliberately not. It only produces structured findings ("red circular rash, mild inflammation, no bleeding"). Those findings are then treated exactly like a text symptom and run through the same RAG/KG/Guardrail pipeline, keeping the final answer grounded rather than trusting the vision model's raw interpretation.

**17. What's OCR for, separately from Vision LLM?**
OCR extracts machine-readable text from scanned documents (prescriptions, lab reports) so they can be indexed and searched — it's a text-extraction step, not an image-understanding step.

---

## Orchestration

**18. What's the difference between LangChain and LangGraph in your project?**
LangChain provides the building blocks inside each agent — prompt templates, the ChromaDB retriever, OpenAI integration, output parsing. LangGraph is the orchestration layer on top that decides *which* agents run for a given request and in what order.

**19. Why not just run every component for every request?**
Latency and cost. A plain text question doesn't need Vision or OCR to execute. LangGraph conditionally routes based on request type instead of running the full pipeline every time.

---

## Prompt Building & OpenAI Integration

**20. Why not just send the user's question straight to ChatGPT?**
A raw question has no domain grounding. The Prompt Builder merges the query with extracted symptoms, the classifier's prediction, retrieved RAG documents, KG relationships, and conversation history into one structured prompt.

**21. How do you keep the OpenAI API key secure?**
Stored in environment variables on the backend, never exposed to the frontend or hardcoded — all API calls happen server-side only.

---

## Safety Guardrails

**22. How do you keep the chatbot from giving unsafe medical advice?**
A Safety Guardrail Engine runs after severity assessment and before the response is returned. If symptoms match a predefined high-risk list — chest pain, breathing difficulty, severe bleeding, stroke signs — the system skips self-diagnosis entirely and returns a fixed escalation message instead of an LLM-generated answer.

---

## Memory, Auth, History

**23. What's the difference between Conversation Memory and Chat History?**
Memory is short-lived, scoped to the active session, and exists purely to give the model context for follow-up questions. History is permanent storage in MongoDB so a user can log back in and revisit a past conversation.

**24. Why use JWT instead of server-side sessions?**
Stateless authentication — no session store to maintain, and it scales more naturally if the backend were split into multiple instances later.

---

## Evaluation

**25. How did you know the chatbot was actually good, not just "working"?**
I built an evaluation set of 100+ representative queries — symptoms, medications, follow-ups, image and document questions, emergency scenarios — and manually checked each response against what was actually retrieved, flagging anything unsupported as a hallucination.
