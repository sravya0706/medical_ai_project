"""
Generates a synthetic symptom-disease dataset for training/demo purposes.

HONESTY NOTE: The original architecture references a public Kaggle
symptom-disease dataset. This sandbox has no network access to Kaggle,
so this script generates a structurally equivalent synthetic dataset
instead — same binary-symptom-feature format, same modeling problem,
but NOT the real Kaggle data. Swap in the real CSV before using this
for anything beyond a local demo (see README).
"""
import random
import pandas as pd

random.seed(42)

SYMPTOMS = [
    "fever", "cough", "headache", "fatigue", "sore_throat",
    "runny_nose", "body_ache", "nausea", "vomiting", "diarrhea",
    "shortness_of_breath", "chest_pain", "dizziness", "rash", "joint_pain",
]

# Disease -> symptoms that are characteristically present (used to bias sampling)
DISEASE_PROFILES = {
    "Influenza": ["fever", "cough", "body_ache", "fatigue", "headache"],
    "Common Cold": ["runny_nose", "sore_throat", "cough", "fatigue"],
    "COVID-19": ["fever", "cough", "shortness_of_breath", "fatigue", "headache"],
    "Migraine": ["headache", "nausea", "dizziness"],
    "Food Poisoning": ["nausea", "vomiting", "diarrhea", "fatigue"],
    "Gastroenteritis": ["diarrhea", "vomiting", "nausea", "fever"],
    "Dengue": ["fever", "joint_pain", "rash", "headache", "fatigue"],
    "Bronchitis": ["cough", "chest_pain", "shortness_of_breath", "fatigue"],
    "Allergic Rhinitis": ["runny_nose", "sore_throat", "rash"],
    "Viral Fever": ["fever", "body_ache", "headache", "fatigue"],
}


def generate_row(disease: str) -> dict:
    profile = set(DISEASE_PROFILES[disease])
    row = {}
    for symptom in SYMPTOMS:
        if symptom in profile:
            # characteristic symptom: present most of the time
            row[symptom] = 1 if random.random() < 0.82 else 0
        else:
            # non-characteristic symptom: rare noise
            row[symptom] = 1 if random.random() < 0.05 else 0
    row["Disease"] = disease
    return row


def build_dataset(rows_per_disease: int = 150) -> pd.DataFrame:
    rows = []
    for disease in DISEASE_PROFILES:
        for _ in range(rows_per_disease):
            rows.append(generate_row(disease))
    df = pd.DataFrame(rows)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


if __name__ == "__main__":
    df = build_dataset()
    df.to_csv("data/symptom_disease_dataset.csv", index=False)
    print(f"Generated dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(df["Disease"].value_counts())
