# Fresher Interview — Questions & Answers (Categories 1–4 + Tell Me About Yourself)

**Important note before you use this:** For the personal/background questions (Tell Me About Yourself, the pivot story, and most behavioral questions), I don't have your real details about 2017–now, so I've built these as **fill-in-the-blank frameworks** with `[bracketed placeholders]` rather than inventing a fake history. Replace every bracket with your actual truth before using these — a fabricated but polished answer is far riskier in an interview than an honest, well-structured real one. The fundamentals (Category 2) and certification questions (Category 4) are answered in full since they're factual, not personal.

---

## 0. Tell Me About Yourself (this sets up everything else)

**Framework — 4 parts, ~60-90 seconds total:**

> "I did my B.Tech in Civil Engineering, graduating in 2017. [ONE honest sentence about what you did in the years after — e.g., 'I worked in X for a few years' / 'I was doing Y' / 'I took time for Z' — whatever is true]. Over the last [timeframe], I got increasingly drawn to AI — specifically how language models and retrieval systems work — and I started learning it seriously through self-study and a Coursera AI certification. To make that learning concrete rather than just theoretical, I built MediAssist, a full-stack medical AI chatbot with RAG, a knowledge graph, vision and OCR pipelines, and safety guardrails — something I could actually defend end-to-end rather than a tutorial project. That's what's brought me here — I'm looking for an entry-level AI engineering role where I can keep building on that foundation in a real team environment."

**Why this structure works:**
- Opens with the fact they'll see on your resume anyway (Civil Engineering) instead of hoping they don't notice
- Fills the gap in one sentence, not ten — a short honest answer reads as confident; a long one reads as anxious
- Pivots quickly to what you *did* about the interest (self-study → cert → project), which is the actual evidence of initiative
- Ends forward-looking, not apologetic

**What NOT to do:** Don't say "I'm just a fresher" or "I don't have much experience" unprompted — let the resume speak for itself and lead with what you *do* have (the project, the initiative, the specific technical depth).

---

## Category 1 — The Pivot Story

**Q1. Walk me through your background — Civil Engineering to AI is a big jump.**

> "I graduated in Civil Engineering in 2017. [Fill in: what you actually did next — worked, freelanced, family reasons, explored other things, etc.]. Somewhere along the way I got pulled toward software and specifically AI — I found I enjoyed the problem-solving side of it more than [reason tied to civil engineering, if true — e.g., site work / the pace of it / whatever's honest]. So I started self-teaching seriously, did a Coursera AI certification, and built a full production-style AI project to prove I could actually apply it, not just understand it conceptually."

**Q2. What made you switch fields?**

> "It wasn't a single moment — more that I kept being drawn to [specific thing: how software could solve problems faster/at scale/etc. — pick what's genuinely true for you]. Civil Engineering taught me to think in systems and constraints, which actually transfers surprisingly well to software architecture — you're always balancing tradeoffs against real limits. AI specifically appealed to me because [genuine reason — e.g., language and reasoning systems, or the pace of the field, or a specific use case that got you interested]."

**Q3. What have you been doing since 2017?** *(Prepare this one most carefully — see note below.)*

> [This needs your real, specific, one-to-two-sentence answer. Whatever it is — another job, a business, family responsibilities, further study, health, anything — state it plainly and move forward. Avoid vague non-answers like "various things" or "figuring things out," which invite more follow-up questions. A specific, closed answer ends the topic; a vague one extends it.]

**Q4. Why AI specifically, not general software development?**

> "I did consider general software development, but what actually held my attention was [genuine reason: e.g., 'how these systems reason over language and retrieve information' or 'the fact that this field is still being figured out in real time']. Building MediAssist confirmed that for me — the parts I found most engaging weren't the CRUD/API plumbing, they were designing the RAG pipeline, figuring out why the model was hallucinating, and tuning retrieval — that's specifically AI engineering work, not general backend work."

**Q5. How did you learn this without a CS degree — self-study, bootcamp, courses?**

> "Mostly structured self-study — I did a Coursera AI certification for foundational grounding, then learned the applied side by building. I don't think a formal CS degree is the only path into this anymore, especially for applied AI engineering versus AI research — the field moves fast enough that hands-on building with the current tools often teaches you more directly relevant skills than a traditional curriculum would."

**Q6. What was the hardest part of learning AI/ML as a non-CS background person?**

> "Honestly, the hardest part wasn't the AI concepts themselves — it was the software engineering fundamentals underneath them: proper API design, database modeling, auth, deployment. AI tutorials often skip that and just show you a Jupyter notebook. Building MediAssist as a full production-style app, not just a model, forced me to actually learn those fundamentals properly — JWT auth, layered backend architecture, database design — alongside the AI-specific pieces."

**Q7. Since you don't have professional experience, how do we know you can work in a real team/production environment?**

> "That's a fair question — I can't point to team experience yet. What I can point to is that I didn't build a toy project; I built something with the concerns a real team would care about: authentication, error handling, security guardrails, an evaluation process, layered architecture for maintainability. I approached it the way I'd want a teammate to approach a real feature, specifically so the gap between 'personal project' and 'production mindset' would be smaller than it usually is for a first project."

---

## Category 2 — Fundamentals (fully answered — these are factual, not personal)

### Python / Programming

**Q8. Difference between list, tuple, set, and dictionary — when would you use each?**
> List: ordered, mutable, allows duplicates — use for a sequence you'll modify (e.g., collecting extracted symptoms). Tuple: ordered, immutable — use for fixed data you don't want changed (e.g., coordinates, a fixed config pair). Set: unordered, unique elements only — use when you need fast membership checks or to deduplicate (e.g., unique symptom names). Dictionary: key-value pairs — use when you need fast lookup by a key (e.g., mapping symptom → severity score).

**Q9. What is a decorator?**
> A function that wraps another function to extend its behavior without modifying its code — e.g., `@app.route()` in Flask or `@router.post()` in FastAPI are decorators that register a function as a request handler. I've used decorators mainly through frameworks rather than writing many custom ones myself.

**Q10. Difference between `is` and `==`?**
> `==` checks value equality (do these two things contain the same data). `is` checks identity (are these the literal same object in memory). Two separate lists with identical contents are `==` but not `is`.

**Q11. What are `*args` and `**kwargs`?**
> `*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword arguments into a dictionary. Useful for writing flexible function signatures — e.g., a wrapper function that passes arguments through to another function without needing to know its exact signature.

**Q12. Mutable vs immutable types, with an example.**
> Mutable objects can be changed after creation (lists, dicts) — modifying one affects every reference to it. Immutable objects can't be changed (strings, tuples, ints) — any "modification" actually creates a new object. This matters for default function arguments — using a mutable default like `def f(x=[])` is a classic bug because that list persists across calls.

**Q13. What's a generator, and why use one over a list?**
> A generator produces values one at a time, lazily, using `yield`, instead of building the whole sequence in memory at once. Useful for processing large datasets or streams — e.g., processing document chunks one at a time during embedding generation instead of loading every chunk into memory simultaneously.

### OOP

**Q14. Explain the four pillars of OOP with a simple example.**
> Encapsulation — bundling data and methods together, hiding internal state (e.g., a `Classifier` class exposing `.predict()` but hiding the model internals). Abstraction — exposing only what's necessary, hiding implementation complexity. Inheritance — a class reusing/extending another's behavior (e.g., a base `Agent` class that `VisionAgent` and `OCRAgent` both extend). Polymorphism — different classes responding to the same method call differently (e.g., every agent has a `.run()` method, but each implements it differently).

**Q15. Difference between an abstract class and an interface concept in Python?**
> Python doesn't have a formal `interface` keyword like Java — it uses abstract base classes (`ABC` from the `abc` module) to define methods that subclasses must implement. An abstract class can have some concrete implementation too, while a pure interface (in languages that have them) typically can't.

**Q16. Method overriding vs overloading?**
> Overriding: a subclass redefines a method that exists in its parent class with the same signature. Overloading: multiple methods with the same name but different parameters — Python doesn't support true overloading like Java/C++; you typically simulate it with default arguments or `*args`.

### SQL / Databases

**Q17. Write a query to find duplicate rows in a table.**
```sql
SELECT email, COUNT(*)
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

**Q18. Difference between `INNER JOIN` and `LEFT JOIN`?**
> `INNER JOIN` returns only rows with matches in both tables. `LEFT JOIN` returns all rows from the left table, with `NULL`s filled in where there's no match in the right table — useful when you want every record from one side regardless of whether it has a related record.

**Q19. What's normalization, and why does it matter?**
> Organizing relational data to reduce redundancy — splitting data into related tables instead of repeating it, using foreign keys to connect them. Matters because it prevents update anomalies (changing a value in one place but missing duplicates elsewhere) and keeps storage efficient.

**Q20. Difference between SQL and NoSQL — when would you pick one over the other?**
> SQL databases (PostgreSQL, MySQL) enforce a fixed schema and strong relational integrity — good for structured data with clear relationships, like financial transactions. NoSQL databases (MongoDB) are schema-flexible and better suited to nested, evolving, or document-shaped data. I used MongoDB for chat conversations specifically because a conversation with a variable-length array of messages fits a document model more naturally than normalizing it across relational tables.

### Core ML Fundamentals

**Q21. Supervised vs unsupervised vs reinforcement learning?**
> Supervised: learning from labeled input-output pairs (e.g., symptom → disease). Unsupervised: finding structure in unlabeled data (e.g., clustering patients by symptom similarity with no predefined labels). Reinforcement: an agent learns by taking actions and receiving rewards/penalties over time, not from a fixed labeled dataset.

**Q22. What's overfitting, and how do you detect/prevent it?**
> The model learns the training data too specifically, including its noise, and performs poorly on new/unseen data. Detected by a large gap between training accuracy and test accuracy. Prevented via train/test splits, cross-validation, regularization, early stopping, or simply more/more-diverse training data.

**Q23. Explain precision, recall, and F1-score — when would you prioritize one over another?**
> Precision: of everything the model predicted positive, how much was actually correct (minimizes false positives). Recall: of everything actually positive, how much did the model catch (minimizes false negatives). F1: harmonic mean of the two, useful when you need a single balanced number. In a medical context, recall often matters more than precision for serious conditions — missing a real case (false negative) is usually worse than a false alarm (false positive) that gets a doctor to double-check.

**Q24. What's the bias-variance tradeoff?**
> Bias is error from overly simplistic assumptions (underfitting); variance is error from being overly sensitive to training data specifics (overfitting). You're always balancing between a model too rigid to capture real patterns and one too flexible that just memorizes noise — the goal is the sweet spot that generalizes well.

**Q25. What's cross-validation, and why is a single train/test split sometimes not enough?**
> Cross-validation (e.g., k-fold) splits the data into multiple train/test partitions and averages performance across all of them, instead of relying on one lucky or unlucky split. A single split can give a misleadingly high or low accuracy just by chance depending on which rows ended up in the test set — cross-validation gives a more reliable estimate.

**Q26. Difference between classification and regression?**
> Classification predicts a discrete category (disease A vs B vs C). Regression predicts a continuous numeric value (e.g., predicting a lab value or risk score). My symptom classifier is a classification problem — predicting a disease label, not a number.

### NLP / GenAI Fundamentals

**Q27. What is a token, and how does tokenization work at a basic level?**
> A token is a chunk of text a model processes — often a word, part of a word, or punctuation mark, not necessarily a whole word. Tokenization breaks input text into these chunks using a fixed vocabulary the model was trained with, so "unbelievable" might become multiple sub-word tokens rather than one.

**Q28. What is an embedding, in plain terms?**
> A way of representing text as a list of numbers (a vector) such that texts with similar meaning end up numerically close together. It lets a computer compare meaning mathematically instead of just comparing exact words.

**Q29. Difference between an LLM and older NLP approaches (rule-based, statistical)?**
> Rule-based NLP relies on hand-written patterns and grammar rules — brittle and doesn't generalize well. Statistical NLP (like older classifiers) learns patterns from data but usually needs heavy feature engineering. LLMs learn language patterns directly from massive amounts of text using deep neural networks (transformers), generalizing far better to new phrasing without needing hand-crafted rules.

**Q30. What is a transformer, at a conceptual level?**
> An architecture that processes all words in a sequence in parallel (unlike older RNNs which processed word-by-word in order) and uses an "attention" mechanism to weigh how much each word should focus on every other word in the sequence. This lets it capture long-range relationships in text efficiently and train much faster than sequence-by-sequence models.

**Q31. What's prompt engineering? Give an example of a poor vs well-written prompt.**
> The practice of structuring instructions to an LLM to get more reliable, accurate output. Poor: "Tell me about this patient's symptoms." (vague, no constraints). Better: "Given only the retrieved medical context below, summarize the patient's likely condition. If the context doesn't contain enough information, say so explicitly rather than guessing." — the second version constrains scope, format, and behavior on uncertainty.

**Q32. What's hallucination in an LLM, and how do you mitigate it?**
> When a model generates plausible-sounding but false or unsupported information. Mitigation strategies: grounding responses in retrieved data (RAG) instead of relying on the model's internal knowledge, constraining the prompt to only answer from provided context, lowering temperature for more deterministic output, and evaluating outputs against real sources to catch and fix hallucination patterns — which is exactly what I did in MediAssist, testing against 100+ queries and refining the prompt and retrieval settings based on what I found.

---

## Category 3 — Behavioral Questions

**Q33. You've only built one project — how do we know this generalizes to real work?**

> "It's a fair concern with just one project — what I'd point to is the *breadth* of that one project rather than its count. It wasn't a single-notebook model demo; it covered auth, database design, API architecture, multi-agent orchestration, safety systems, and evaluation — the same categories of problems a real production feature would touch. I built it specifically to be broad enough to demonstrate range, not just depth in one narrow skill."

**Q34. What would you do in your first 90 days if we hired you?**

> "First few weeks, I'd focus on understanding the existing codebase, tooling, and team conventions rather than trying to make an impact too early — asking a lot of questions and pairing where possible. By 30-60 days, I'd want to be shipping small, well-scoped tasks independently. By 90 days, I'd hope to be contributing to something with more ownership, ideally something that lets me apply what I built in MediAssist — RAG, evaluation, or agent orchestration work specifically."

**Q35. How do you stay updated in a field that changes this fast?**

> "I follow [fill in real sources you actually use — specific newsletters, papers, Twitter/X accounts, Anthropic/OpenAI release notes, etc.]. More concretely though, I try to actually build with new tools rather than just read about them — that's part of why the project used LangGraph, which was newer at the time I was building, rather than sticking with a simpler sequential pipeline the whole way through."

**Q36. Tell me about a time you were stuck on a technical problem — what did you do?**

> [Use a real MediAssist debugging story here — e.g., the hallucination issue where the model recommended antibiotics not in retrieved documents. Structure: what was the symptom of the bug → how you isolated the cause → what you changed → how you verified the fix. Example: "During evaluation, I found the chatbot recommending antibiotics that weren't in any retrieved document. I traced it back to the system prompt allowing the model to fall back on general knowledge when context felt thin. I tightened the prompt to explicitly forbid answering outside retrieved context and increased the RAG chunk size slightly, then reran the same 100 test queries to confirm the fix actually worked rather than assuming it did."]

**Q37. What's your expected salary?**

> [This needs real research on your part — check current entry-level AI engineer salary bands for your target companies and location (India, given your context) before this comes up. A safe framework: "I'm looking for a fair offer aligned with market rate for an entry-level AI engineering role in [location] — I'm flexible and more focused on finding the right team and learning opportunity at this stage." Avoid naming a number first if you can defer it, but have a realistic range ready if pressed.]

**Q38. Are you open to relocating / this being an in-office role?**

> [Answer honestly based on your actual constraints — a vague or evasive answer here just delays a logistics conversation that needs to happen anyway.]

**Q39. Why should we hire you over a CS-degree fresher with similar project experience?**

> "I'd actually frame the Civil Engineering background as an asset, not a gap to explain away. It means I approached this AI project the way someone building real infrastructure does — thinking about failure modes, safety constraints, and systems that need to work reliably, not just impressively in a demo. The safety guardrail layer and evaluation process in MediAssist weren't afterthoughts — they came from that same instinct of 'what happens when this is wrong and someone relies on it.' That's a mindset, not just a skillset, and I think it transfers."

---

## Category 4 — Certification Questions

**Q40. What did your Coursera AI certification actually cover?**

> [Fill in with the real syllabus/topics from the specific Coursera course you completed — course name, instructor/institution if notable, and 2-3 specific modules or topics it covered, e.g., supervised learning fundamentals, neural network basics, NLP foundations, etc.]

**Q41. Can you name a specific concept from it you found difficult?**

> [Pick something real and specific — e.g., "the math behind backpropagation took me a few passes to really internalize" or "understanding attention mechanisms conceptually before I'd actually used a transformer-based model took some time." A specific, honestly-difficult concept reads as far more credible than claiming everything was easy.]

**Q42. How did you apply what you learned in the certification to your project?**

> "The certification gave me the conceptual grounding — how models are trained, what embeddings and retrieval actually mean, core NLP concepts. MediAssist is where I applied that practically — for example, understanding *why* RAG reduces hallucination conceptually from the course is different from actually tuning chunk size and prompt constraints until you can measure the hallucination rate dropping, which is what I did in the project."

---

## Final Prep Note

The single highest-leverage thing to do before any interview using this doc: **fill in every bracketed placeholder with your real, specific truth** — especially Q3 ("what have you been doing since 2017"). A generic or evasive answer to that one question colors how the interviewer hears everything else you say afterward, even the strong technical answers above.
