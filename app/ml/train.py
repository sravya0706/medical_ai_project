"""
Trains the XGBoost symptom classifier and saves it + evaluation metrics.
Run: python3 -m app.ml.train
"""
import json
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

from app.config import settings


def train():
    df = pd.read_csv("data/symptom_disease_dataset.csv")

    X = df.drop(columns=["Disease"])
    y_raw = df["Disease"]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        eval_metric="mlogloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "precision_weighted": precision_score(y_test, preds, average="weighted", zero_division=0),
        "recall_weighted": recall_score(y_test, preds, average="weighted", zero_division=0),
        "f1_weighted": f1_score(y_test, preds, average="weighted", zero_division=0),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    joblib.dump(model, settings.classifier_model_path)
    joblib.dump(label_encoder, "./data/label_encoder.pkl")
    with open(settings.classifier_columns_path, "w") as f:
        json.dump(list(X.columns), f)
    with open("./data/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Training complete. Held-out test set metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    return metrics


if __name__ == "__main__":
    train()
