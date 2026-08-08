from fastapi import APIRouter, Depends, UploadFile, File, Form

from app.schemas import ChatResponse
from app.auth.dependencies import get_current_user_id
from app.agents.orchestrator import run_pipeline
from app.memory.session_memory import add_turn
from app.memory.conversation_map import get_conversation_id, set_conversation_id
from app.db.mongo_client import is_mongo_available, create_conversation, append_message
from app.routes.upload_validation import validate_and_encode_image

router = APIRouter(prefix="/api/v1/vision", tags=["vision"])


@router.post("/upload", response_model=ChatResponse)
async def upload_image(
    file: UploadFile = File(...),
    message: str = Form(default="Can you tell me what this looks like?"),
    session_id: str = Form(default="default"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Image uploads enter the same LangGraph pipeline as a text query. OCR
    runs first: document-like uploads use only PII-redacted OCR text for
    RAG/LLM processing, while images without readable text continue to the
    Vision LLM path.
    """
    print(
        f"[vision][{session_id}] Upload received "
        f"(filename={file.filename!r}, content_type={file.content_type!r}, "
        f"message_chars={len(message)})"
    )
    image_b64 = await validate_and_encode_image(file)
    print(f"[vision][{session_id}] Image validated and encoded (base64_chars={len(image_b64)})")

    add_turn(session_id, "user", f"{message} [uploaded image: {file.filename}]")
    result = run_pipeline(session_id, message, image_b64=image_b64)

    if result.get("response"):
        add_turn(session_id, "assistant", result["response"])

    if is_mongo_available():
        try:
            conversation_id = get_conversation_id(session_id)
            if not conversation_id:
                conversation_id = create_conversation(user_id, title=f"[Image] {message[:40]}")
                set_conversation_id(session_id, conversation_id)
            append_message(conversation_id, "user", f"{message} [uploaded image: {file.filename}]")
            if result.get("response"):
                append_message(conversation_id, "assistant", result["response"])
            print(f"[history][{session_id}] Vision conversation persisted (conversation_id={conversation_id})")
        except Exception as e:
            print(f"[history] Could not persist vision conversation: {e}")
    else:
        print("[history] MongoDB unreachable — vision response returned but not persisted.")

    print(
        f"[vision][{session_id}] Response ready "
        f"(escalated={result.get('escalated', False)}, "
        f"ocr_text={result.get('ocr_text_extracted', False)}, "
        f"ocr_error={bool(result.get('ocr_error'))}, "
        f"vision_error={bool(result.get('vision_error'))}, "
        f"sources={len(result.get('sources', []))})"
    )

    return ChatResponse(
        success=True,
        response=result.get("response"),
        escalated=result.get("escalated", False),
        predicted_conditions=result.get("predicted_conditions", []),
        sources=result.get("sources", []),
        error=result.get("error") or result.get("vision_error"),
    )
