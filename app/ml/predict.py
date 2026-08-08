"""
Loads the trained XGBoost model once and exposes a predict function.
"""
import json
import joblib
import pandas as pd

from app.config import settings

_model = None
_label_encoder = None
_columns = None


def _load():
    global _model, _label_encoder, _columns
    if _model is None:
        print("[ml] Loading classifier artifacts")
        _model = joblib.load(settings.classifier_model_path)
        _label_encoder = joblib.load("./data/label_encoder.pkl")
        with open(settings.classifier_columns_path) as f:
            _columns = json.load(f)
        print(f"[ml] Classifier ready (feature_count={len(_columns)})")
    return _model, _label_encoder, _columns


def predict_conditions(symptom_flags: dict, top_n: int = 3) -> list[dict]:
    """
    symptom_flags: dict like {"fever": 1, "cough": 1, ...} — missing keys default to 0.
    Returns top_n predicted conditions with confidence scores.
    """
    model, label_encoder, columns = _load()

    row = {col: symptom_flags.get(col, 0) for col in columns}
    X = pd.DataFrame([row], columns=columns)

    probabilities = model.predict_proba(X)[0]
    top_indices = probabilities.argsort()[::-1][:top_n]

    results = []
    for idx in top_indices:
        disease = label_encoder.inverse_transform([idx])[0]
        results.append({
            "condition": disease,
            "confidence": round(float(probabilities[idx]), 4)
        })
    print(f"[ml] Prediction complete (input_symptoms={list(symptom_flags)}, results={results})")
    return results


if __name__ == "__main__":
    # quick manual smoke test
    example = {"fever": 1, "cough": 1, "body_ache": 1, "fatigue": 1}
    print(predict_conditions(example))
