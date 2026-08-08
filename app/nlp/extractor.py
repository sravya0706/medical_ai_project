"""
Rule-based symptom extraction from free text.

HONESTY NOTE: this is a keyword/phrase-matching extractor, not a trained
NER model — it's a real, working, defensible implementation choice for a
personal project's scale, but you should describe it as such in
interviews rather than implying a trained NLP model. A production
upgrade path (spaCy NER / a fine-tuned extraction model) is noted in
the README.
"""
import re

# symptom_key -> list of natural-language phrases that indicate it
SYMPTOM_LEXICON = {
    "fever": ["fever", "high temperature", "temperature", "burning up"],
    "cough": ["cough", "coughing"],
    "headache": ["headache", "head ache", "head pain", "migraine"],
    "fatigue": ["fatigue", "tired", "exhausted", "no energy", "weak"],
    "sore_throat": ["sore throat", "throat pain", "throat hurts"],
    "runny_nose": ["runny nose", "stuffy nose", "blocked nose", "congestion"],
    "body_ache": ["body ache", "body pain", "muscle pain", "aches all over"],
    "nausea": ["nausea", "nauseous", "feel sick", "queasy"],
    "vomiting": ["vomit", "vomiting", "throwing up"],
    "diarrhea": ["diarrhea", "loose motion", "loose motions", "stomach upset"],
    "shortness_of_breath": ["shortness of breath", "can't breathe", "cant breathe",
                             "difficulty breathing", "breathless"],
    "chest_pain": ["chest pain", "chest tightness", "pain in chest"],
    "dizziness": ["dizziness", "dizzy", "lightheaded"],
    "rash": ["rash", "skin rash", "red spots", "itchy skin"],
    "joint_pain": ["joint pain", "joints hurt", "joint ache"],
}

# duration patterns: "3 days", "two weeks", "since yesterday"
DURATION_PATTERN = re.compile(
    r"(\d+|one|two|three|four|five|six|seven)\s+(days|day|weeks|week|hours|hour)",
    re.IGNORECASE,
)


def extract_symptoms(text: str) -> dict:
    """
    Returns:
      {
        "symptoms": {"fever": 1, "cough": 1},   # binary flags for classifier
        "matched_phrases": ["fever", "cough"],   # what was actually found, for debugging
        "duration": "3 days" | None
      }
    """
    text_lower = text.lower()
    symptom_flags = {}
    matched_phrases = []

    for symptom_key, phrases in SYMPTOM_LEXICON.items():
        for phrase in phrases:
            if phrase in text_lower:
                symptom_flags[symptom_key] = 1
                matched_phrases.append(phrase)
                break  # one match per symptom is enough

    duration_match = DURATION_PATTERN.search(text_lower)
    duration = duration_match.group(0) if duration_match else None

    result = {
        "symptoms": symptom_flags,
        "matched_phrases": matched_phrases,
        "duration": duration,
    }
    print(
        "[nlp] Extraction complete "
        f"(symptoms={list(symptom_flags)}, matched={matched_phrases}, duration={duration!r})"
    )
    return result


def needs_followup(extraction: dict, min_symptoms: int = 2) -> bool:
    """If too few symptoms were extracted, the chatbot should ask a follow-up
    question before attempting classification — matches documented
    Conversation Memory / multi-turn behavior."""
    return len(extraction["symptoms"]) < min_symptoms


if __name__ == "__main__":
    sample = "I've had a fever and cough for three days, feeling really tired too."
    result = extract_symptoms(sample)
    print(result)
    print("Needs follow-up?", needs_followup(result))
