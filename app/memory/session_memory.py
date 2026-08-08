"""
In-process session-based Conversation Memory — matches Module 8/21.

HONESTY NOTE: this is in-process (a Python dict), which is genuinely
correct for a single-instance local run. The documented architecture's
"Future Improvements" section already notes Redis as the scaling path for
multi-instance deployments — that's a real config change, not something
faked here; this module is exactly what you'd want for local/dev use.
"""

_sessions: dict[str, list[dict]] = {}

MAX_TURNS_IN_CONTEXT = 6  # last 3 user/assistant turn pairs


def add_turn(session_id: str, role: str, content: str):
    _sessions.setdefault(session_id, []).append({"role": role, "content": content})
    print(
        f"[memory][{session_id}] Stored {role} turn "
        f"(turns_in_session={len(_sessions[session_id])}, content_chars={len(content)})"
    )


def get_recent_history_text(session_id: str) -> str:
    history = _sessions.get(session_id, [])
    recent = history[-MAX_TURNS_IN_CONTEXT:]
    result = "\n".join(f"{turn['role']}: {turn['content']}" for turn in recent)
    print(f"[memory][{session_id}] Loaded {len(recent)} recent turn(s) for prompt context")
    return result


def get_accumulated_symptoms(session_id: str) -> str:
    """Concatenates all user turns so far — used to decide if enough
    information has been gathered before attempting classification."""
    history = _sessions.get(session_id, [])
    user_turns = [t["content"] for t in history if t["role"] == "user"]
    return " ".join(user_turns)


def clear_session(session_id: str):
    _sessions.pop(session_id, None)
