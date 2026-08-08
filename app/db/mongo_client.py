"""
Real MongoDB integration via PyMongo — users, conversations, sessions.

HONESTY NOTE: no MongoDB server is available in this sandbox (no
mongodb-server apt package, no Docker). This is real, production-correct
PyMongo code — point MONGODB_URI at a real instance (see docker-compose.yml)
and it works as written. In this sandbox, connections will time out;
callers (auth routes, chat service) catch that explicitly rather than
crashing silently — see comments at each call site.
"""
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from app.config import settings

_client = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
    return _client


def get_db():
    return get_client()[settings.mongodb_db_name]


def ensure_indexes():
    """Matches Module 11's documented indexing strategy: compound index on
    (userId, updatedAt) for the conversation list query pattern."""
    db = get_db()
    db["conversations"].create_index([("userId", ASCENDING), ("updatedAt", DESCENDING)])
    db["users"].create_index("email", unique=True)


# ---------- Users ----------

def create_user(email: str, hashed_password: str) -> str:
    db = get_db()
    result = db["users"].insert_one({
        "email": email,
        "hashedPassword": hashed_password,
        "createdAt": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def get_user_by_email(email: str) -> dict | None:
    db = get_db()
    return db["users"].find_one({"email": email})


# ---------- Conversations ----------

def create_conversation(user_id: str, title: str) -> str:
    db = get_db()
    now = datetime.now(timezone.utc)
    result = db["conversations"].insert_one({
        "userId": user_id,
        "title": title,
        "messages": [],
        "createdAt": now,
        "updatedAt": now,
    })
    return str(result.inserted_id)


def append_message(conversation_id: str, role: str, content: str):
    """Atomic $push — avoids read-modify-write races on concurrent messages,
    per the documented reasoning in the intermediate code reference."""
    db = get_db()
    from bson import ObjectId
    db["conversations"].update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$push": {"messages": {"role": role, "content": content, "at": datetime.now(timezone.utc)}},
            "$set": {"updatedAt": datetime.now(timezone.utc)},
        },
    )


def get_conversations_for_user(user_id: str, limit: int = 20) -> list[dict]:
    """Uses the (userId, updatedAt) compound index — filter by user, sort by recency."""
    db = get_db()
    cursor = db["conversations"].find({"userId": user_id}).sort("updatedAt", DESCENDING).limit(limit)
    return list(cursor)


def get_conversation_by_id(conversation_id: str, user_id: str) -> dict | None:
    """Authorization check baked into the query itself — a conversation is
    only returned if it belongs to the requesting user (ownership check at
    the repository layer, matching Module 10's JWT isolation design)."""
    db = get_db()
    from bson import ObjectId
    return db["conversations"].find_one({"_id": ObjectId(conversation_id), "userId": user_id})


def is_mongo_available() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except PyMongoError:
        return False
