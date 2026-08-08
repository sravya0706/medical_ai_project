"""
Central configuration. Everything is read from environment variables / .env —
nothing is hardcoded. Copy .env.example to .env and fill in real values.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- MongoDB ---
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "mediassist"

    # --- Neo4j ---
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # --- OpenAI ---
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4o"
    llm_temperature: float = 0.3

    # --- Auth ---
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # --- RAG ---
    chroma_persist_dir: str = "./data/chroma_db"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    rag_top_k: int = 4
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 100

    # --- Classifier ---
    classifier_model_path: str = "./data/model.pkl"
    classifier_columns_path: str = "./data/model_columns.json"

    # --- Uploads ---
    upload_dir: str = "./data/uploads"
    max_upload_mb: int = 10
    # --- CORS ---
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()
