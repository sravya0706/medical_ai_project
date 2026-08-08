from fastapi import APIRouter, Depends, HTTPException
from bson.errors import InvalidId

from app.schemas import ChatRequest, ChatResponse
from app.auth.dependencies import get_current_user_id
from app.agents.orchestrator import run_pipeline
from app.memory.session_memory import add_turn
from app.memory.conversation_map import get_conversation_id, set_conversation_id
from app.db.mongo_client import (
    is_mongo_available, create_conversation, append_message,
    get_conversations_for_user, get_conversation_by_id,
)

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, user_id: str = Depends(get_current_user_id)):
    print(
        f"[chat][{payload.session_id}] Request received "
        f"(message_chars={len(payload.message)}, user_id={user_id})"
    )
    add_turn(payload.session_id, "user", payload.message)
    result = run_pipeline(payload.session_id, payload.message)

    if result.get("response"):
        add_turn(payload.session_id, "assistant", result["response"])

    # Best-effort persistence — documented behavior: if MongoDB isn't
    # reachable, the AI response still returns to the caller; only
    # persistence is skipped, with a clear warning, not a silent failure.
    # One conversation thread per session_id, not a new one per message.
    if is_mongo_available():
        try:
            conversation_id = get_conversation_id(payload.session_id)
            if not conversation_id:
                conversation_id = create_conversation(user_id, title=payload.message[:50])
                set_conversation_id(payload.session_id, conversation_id)

            append_message(conversation_id, "user", payload.message)
            if result.get("response"):
                append_message(conversation_id, "assistant", result["response"])
            print(f"[history][{payload.session_id}] Conversation persisted (conversation_id={conversation_id})")
        except Exception as e:
            print(f"[history] Could not persist conversation: {e}")
    else:
        print("[history] MongoDB unreachable — response returned but not persisted.")

    if result.get("error"):
        print(f"[chat][{payload.session_id}] Pipeline failed: {result['error']}")
        raise HTTPException(status_code=503, detail=result["error"])

    print(
        f"[chat][{payload.session_id}] Response ready "
        f"(escalated={result.get('escalated', False)}, "
        f"conditions={len(result.get('predicted_conditions', []))}, "
        f"sources={len(result.get('sources', []))})"
    )

    return ChatResponse(
        success=True,
        response=result.get("response"),
        escalated=result.get("escalated", False),
        predicted_conditions=result.get("predicted_conditions", []),
        sources=result.get("sources", []),
    )


@router.get("/history")
def get_history(user_id: str = Depends(get_current_user_id)):
    if not is_mongo_available():
        raise HTTPException(status_code=503, detail="MongoDB is not reachable.")
    conversations = get_conversations_for_user(user_id)
    for c in conversations:
        c["_id"] = str(c["_id"])
    return {"conversations": conversations}


@router.get("/history/{conversation_id}")
def get_conversation(conversation_id: str, user_id: str = Depends(get_current_user_id)):
    if not is_mongo_available():
        raise HTTPException(status_code=503, detail="MongoDB is not reachable.")
    try:
        convo = get_conversation_by_id(conversation_id, user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid conversation ID.")
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    convo["_id"] = str(convo["_id"])
    return convo
