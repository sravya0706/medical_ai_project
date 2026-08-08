"""
Ingests the knowledge base into a real, embedded ChromaDB collection.

HONESTY NOTE ON EMBEDDINGS: this sandbox has no network access to either
api.openai.com (OpenAI embeddings) or huggingface.co (sentence-transformers
model download), so neither of the two embedding approaches documented in
the architecture can actually download weights here. Rather than silently
fake it, this uses a real, classical, zero-download embedding technique
instead: TF-IDF vectors (scikit-learn), which is a legitimate, well-established
dense-vector text representation — not a stand-in that pretends to be
something else. The vectorizer is fit once on the corpus and persisted, then
reused (transform-only) for queries so the vector space stays consistent.

To use real OpenAI or sentence-transformers embeddings once you have network
access, swap `TfidfEmbeddingFunction` below for
`chromadb.utils.embedding_functions.OpenAIEmbeddingFunction` or
`SentenceTransformerEmbeddingFunction` — the rest of the RAG pipeline
(retriever, prompt builder) does not need to change.

Run: python3 -m app.rag.ingest
"""
import joblib
import chromadb
from chromadb import EmbeddingFunction
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.rag.knowledge_base import DOCUMENTS

VECTORIZER_PATH = "./data/tfidf_vectorizer.pkl"


class TfidfEmbeddingFunction(EmbeddingFunction):
    """Chroma-compatible embedding function backed by a fitted TfidfVectorizer.
    Must call `.fit(corpus)` once during ingestion before use for queries."""

    def __init__(self):
        self.vectorizer: TfidfVectorizer | None = None

    def fit(self, corpus: list[str]):
        self.vectorizer = TfidfVectorizer(max_features=512, stop_words="english")
        self.vectorizer.fit(corpus)
        joblib.dump(self.vectorizer, VECTORIZER_PATH)

    def load(self):
        self.vectorizer = joblib.load(VECTORIZER_PATH)

    def __call__(self, input: list[str]) -> list[list[float]]:
        if self.vectorizer is None:
            self.load()
        matrix = self.vectorizer.transform(input)
        return matrix.toarray().tolist()

    @staticmethod
    def name() -> str:
        return "tfidf_local"

    def get_config(self) -> dict:
        return {"type": "tfidf_local", "path": VECTORIZER_PATH}

    @staticmethod
    def build_from_config(config: dict) -> "TfidfEmbeddingFunction":
        fn = TfidfEmbeddingFunction()
        fn.load()
        return fn


def get_chroma_collection(embedding_fn: TfidfEmbeddingFunction):
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(
        name="medical_docs",
        embedding_function=embedding_fn,
    )
    return collection


def ingest():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
    )

    ids, texts, metadatas = [], [], []
    for doc in DOCUMENTS:
        chunks = splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            ids.append(f"{doc['id']}_chunk{i}")
            texts.append(chunk)
            metadatas.append({"topic": doc["topic"], "source_id": doc["id"]})

    # Fit the TF-IDF vectorizer on the actual chunk corpus first, then persist it
    embedding_fn = TfidfEmbeddingFunction()
    embedding_fn.fit(texts)

    collection = get_chroma_collection(embedding_fn)
    # upsert so re-running ingest doesn't duplicate
    collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
    print(f"Ingested {len(ids)} chunks from {len(DOCUMENTS)} source documents.")
    return len(ids)


if __name__ == "__main__":
    ingest()
