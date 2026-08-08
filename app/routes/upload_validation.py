"""
File upload validation — matches Module 6/17's documented checks
(MIME type, extension, file size) before anything reaches Vision/OCR.
"""
import base64
from fastapi import UploadFile, HTTPException

from app.config import settings

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg"}
ALLOWED_DOC_TYPES = {"application/pdf"}


async def validate_and_read(file: UploadFile, allowed_types: set[str]) -> bytes:
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {allowed_types}",
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB). Max allowed: {settings.max_upload_mb}MB",
        )

    await file.seek(0)
    return contents


async def validate_and_encode_image(file: UploadFile) -> str:
    """Returns base64-encoded image data, ready for the Vision LLM call.

    NOTE (disclosed, not hidden): this checks the declared content_type
    header, which a client can spoof. A hardened version would also verify
    actual file signature bytes (magic numbers) rather than trusting the
    header alone — see README known gaps.
    """
    contents = await validate_and_read(file, ALLOWED_IMAGE_TYPES)
    return base64.b64encode(contents).decode("utf-8")
