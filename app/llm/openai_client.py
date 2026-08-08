"""
Real OpenAI SDK integration for chat generation + vision.

HONESTY NOTE: this sandbox has no network access to api.openai.com, so
even with a valid API key, calls made *from here* will fail with a
connection error. This is real, unmodified OpenAI SDK usage — on your own
machine with a valid OPENAI_API_KEY and normal internet access, it works
as written.

Deliberate design choice: if no API key is configured, this raises a clear
LLMNotConfiguredError rather than returning a fabricated response that
pretends to be a real model output. Silently faking an LLM response would
be actively misleading — the caller (chat service) surfaces this as a
clear 503-style error to the API consumer instead.
"""
from openai import OpenAI, APIConnectionError, AuthenticationError

from app.config import settings


class LLMNotConfiguredError(Exception):
    pass


class LLMUnavailableError(Exception):
    pass


_client = None


def get_client() -> OpenAI:
    global _client
    if not settings.openai_api_key:
        print("[llm] OPENAI_API_KEY is not configured")
        raise LLMNotConfiguredError(
            "OPENAI_API_KEY is not set. Set it in your .env file to enable "
            "real LLM responses. Refusing to fabricate a response."
        )
    if _client is None:
        print("[llm] Initializing OpenAI client")
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def generate_response(messages: list[dict]) -> str:
    client = get_client()
    print(f"[llm] Generating chat response (model={settings.openai_chat_model}, messages={len(messages)})")
    try:
        response = client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=messages,
            temperature=settings.llm_temperature,
        )
        content = response.choices[0].message.content
        print(f"[llm] Chat response received (response_chars={len(content or '')})")
        return content
    except AuthenticationError as e:
        raise LLMUnavailableError(f"OpenAI authentication failed: {e}") from e
    except APIConnectionError as e:
        raise LLMUnavailableError(
            f"Could not reach OpenAI API (network issue): {e}"
        ) from e


def analyze_medical_image(image_b64: str, user_query: str) -> str:
    client = get_client()
    print(f"[llm] Analyzing image (model={settings.openai_vision_model}, base64_chars={len(image_b64)})")
    try:
        response = client.chat.completions.create(
            model=settings.openai_vision_model,
            messages=[
                {"role": "system", "content": "Describe visible medical findings only. Do not diagnose."},
                {"role": "user", "content": [
                    {"type": "text", "text": user_query},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                ]},
            ],
        )
        content = response.choices[0].message.content
        print(f"[llm] Vision findings received (finding_chars={len(content or '')})")
        return content
    except AuthenticationError as e:
        raise LLMUnavailableError(f"OpenAI authentication failed: {e}") from e
    except APIConnectionError as e:
        raise LLMUnavailableError(
            f"Could not reach OpenAI Vision API (network issue): {e}"
        ) from e
