"""
MediAssist FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000

Then visit http://localhost:8000/docs for interactive Swagger UI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routes import auth_routes, chat_routes, vision_routes
from app.db.mongo_client import ensure_indexes, is_mongo_available


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if is_mongo_available():
        ensure_indexes()
        print("[startup] MongoDB connected — indexes ensured.")
    else:
        print("[startup] MongoDB not reachable — auth/history endpoints will "
              "return 503 until MONGODB_URI points to a running instance.")
    yield
    # Shutdown (nothing to clean up currently)


app = FastAPI(
    title="MediAssist API",
    description="AI-powered healthcare assistant — RAG + Knowledge Graph + Safety Guardrails",
    version="1.0.0",
    lifespan=lifespan,
)

# Without this, the browser's preflight OPTIONS request (sent automatically
# before any cross-origin POST/PUT/DELETE, or any request with a custom
# header like Authorization) gets no matching route and FastAPI returns
# 405 — which is exactly the error this fixes. curl/Swagger never hit this
# because they don't send a CORS preflight the way a browser does.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(vision_routes.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "mongo_available": is_mongo_available()}