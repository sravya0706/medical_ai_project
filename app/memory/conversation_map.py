"""
Maps a session_id to a single MongoDB conversation_id, so repeated chat
messages within the same session append to one growing conversation
thread instead of creating a new conversation document per message.

HONESTY NOTE: this is in-process (a dict), same characteristics and same
limitations as app/memory/session_memory.py — fine for a single instance,
would need Redis (or storing the mapping in Mongo itself) to survive a
restart or work across multiple backend instances.
"""

_session_to_conversation: dict[str, str] = {}


def get_conversation_id(session_id: str) -> str | None:
    return _session_to_conversation.get(session_id)


def set_conversation_id(session_id: str, conversation_id: str):
    _session_to_conversation[session_id] = conversation_id
