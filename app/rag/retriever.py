"""
RAG retrieval — queries the real ChromaDB collection built by ingest.py.
"""
from app.config import settings
from app.rag.ingest import get_chroma_collection, TfidfEmbeddingFunction

_collection = None
_embedding_fn = None


def _get_collection():
    global _collection, _embedding_fn
    if _collection is None:
        print("[rag] Loading TF-IDF vectorizer and Chroma collection")
        _embedding_fn = TfidfEmbeddingFunction()
        _embedding_fn.load()  # must have been fit during ingest.py
        _collection = get_chroma_collection(_embedding_fn)
        print(f"[rag] Collection ready (document_count={_collection.count()})")
    return _collection


def retrieve(query: str, top_k: int | None = None) -> list[dict]:
    """
    Returns a list of {"text": ..., "topic": ..., "source_id": ..., "distance": ...}
    Empty list if nothing retrieved (e.g. empty collection) — callers must
    handle this by telling the LLM there's insufficient grounded information,
    per the documented hallucination-mitigation prompt rule.
    """
    collection = _get_collection()
    k = top_k or settings.rag_top_k

    if collection.count() == 0:
        print("[rag] Retrieval skipped: collection is empty")
        return []

    results = collection.query(query_texts=[query], n_results=min(k, collection.count()))

    retrieved = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, dists):
        retrieved.append({
            "text": doc,
            "topic": meta.get("topic"),
            "source_id": meta.get("source_id"),
            "distance": dist,
        })
    print(
        f"[rag] Retrieval complete (requested_top_k={k}, returned={len(retrieved)}, "
        f"topics={[item['topic'] for item in retrieved]})"
    )
    return retrieved


if __name__ == "__main__":
    for r in retrieve("I have fever and body aches for two days"):
        print(f"[{r['topic']}] (dist={r['distance']:.3f}) {r['text'][:80]}...")
