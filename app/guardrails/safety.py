"""
Rule-based safety guardrail — matches Module 19 exactly.
"""

HIGH_RISK_PATTERNS = [
    "chest pain", "difficulty breathing", "can't breathe", "cant breathe",
    "severe bleeding", "loss of consciousness", "unconscious", "seizure",
    "stroke", "facial drooping", "slurred speech", "coughing blood",
    "suicidal", "want to die", "overdose",
]


def assess_severity(raw_query: str) -> str:
    query_lower = raw_query.lower()
    for pattern in HIGH_RISK_PATTERNS:
        if pattern in query_lower:
            return "HIGH_RISK"
    return "LOW_RISK"


def apply_guardrail(raw_query: str) -> str | None:
    """Returns an escalation message if high-risk, else None (proceed normally)."""
    severity = assess_severity(raw_query)
    if severity == "HIGH_RISK":
        return (
            "These symptoms may indicate a serious medical condition. "
            "Please seek emergency medical care immediately or contact your local "
            "emergency services. This chatbot cannot diagnose or manage emergencies."
        )
    return None


if __name__ == "__main__":
    print(apply_guardrail("I have mild fever and cough"))
    print(apply_guardrail("I have severe chest pain and difficulty breathing"))
