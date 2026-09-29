from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR / "dataset" / "Crop_recommendation.csv"
)

MODEL_PATH = (
    BASE_DIR / "ml_models" / "crop_recommendation.joblib"
)

FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
]

TARGET = "label"


df = pd.read_csv(DATASET_PATH)

required_columns = FEATURES + [TARGET]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Dataset is missing columns: {missing_columns}"
    )

df = df.dropna(subset=required_columns)

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print(
    "Test accuracy:",
    accuracy_score(y_test, predictions)
)

print(
    classification_report(y_test, predictions)
)

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    {
        "model": model,
        "features": FEATURES,
    },
    MODEL_PATH
)

print("Model saved to:", MODEL_PATH)