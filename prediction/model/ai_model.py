from pathlib import Path

import numpy as np
from django.conf import settings

from .ai.opencv_processor import preprocess_crop_image


# =====================================================
# MODEL
# =====================================================

MODEL_PATH = (
    Path(settings.BASE_DIR)
    / "prediction"
    / "model"
    / "crop_disease_model.keras"
)


# =====================================================
# CLASS NAMES
# =====================================================

CLASS_NAMES = [
    "Healthy",
    "Bacterial Blight",
    "Leaf Blast",
    "Brown Spot",
    "Powdery Mildew",
    "Leaf Rust",
    "Early Blight",
    "Late Blight",
]


# =====================================================
# LOAD MODEL
# =====================================================

_model = None


def get_model():

    global _model

    if _model is not None:
        return _model

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"AI model not found: {MODEL_PATH}"
        )

    if MODEL_PATH.stat().st_size == 0:
        raise ValueError(
            "AI model file is empty. "
            "Please add a trained .keras model."
        )

    from tensorflow.keras.models import load_model

    _model = load_model(
        MODEL_PATH,
        compile=False
    )

    return _model


# =====================================================
# PREDICT
# =====================================================

def predict_disease(image_path):

    model = get_model()

    processed_image = (
        preprocess_crop_image(
            image_path
        )
    )

    predictions = model.predict(
        processed_image,
        verbose=0
    )

    probabilities = predictions[0]

    predicted_index = int(
        np.argmax(probabilities)
    )

    confidence = (
        float(
            probabilities[predicted_index]
        ) * 100
    )

    if predicted_index >= len(CLASS_NAMES):
        raise ValueError(
            "Model output classes do not match "
            "CLASS_NAMES."
        )

    disease_name = CLASS_NAMES[
        predicted_index
    ]

    # Top 3 predictions
    top_indices = np.argsort(
        probabilities
    )[-3:][::-1]

    top_predictions = []

    for index in top_indices:

        if index >= len(CLASS_NAMES):
            continue

        top_predictions.append({
            "disease": CLASS_NAMES[index],
            "confidence": round(
                float(
                    probabilities[index]
                ) * 100,
                2
            )
        })

    # Severity
    if disease_name == "Healthy":
        severity = "Healthy"

    elif confidence >= 80:
        severity = "High"

    elif confidence >= 55:
        severity = "Medium"

    else:
        severity = "Low"

    return {
        "disease_name": disease_name,
        "confidence": round(
            confidence,
            2
        ),
        "severity": severity,
        "top_predictions": top_predictions,
    }