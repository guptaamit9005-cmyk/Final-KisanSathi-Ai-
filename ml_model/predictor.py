"""
Loads the trained crop-disease model once (kept in memory) and exposes
predict_disease() for the Django view to call on every uploaded image.

Expects a model file named crop_disease_model.h5 in this same folder,
trained with train_model.py (or your own equivalent script/dataset).
"""

import os
import numpy as np
from PIL import Image

MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_disease_model.h5")
IMG_SIZE = (224, 224)

# Must match the order of class_indices used during training.
# train_model.py prints this out after training — copy it here exactly.
CLASS_NAMES = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_healthy",
]

_model = None


def get_model():
    """Lazily load the model once per process, then reuse it."""
    global _model
    if _model is None:
        from tensorflow.keras.models import load_model
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                "Run train_model.py first, or place your trained "
                "crop_disease_model.h5 in the ml_model/ folder."
            )
        _model = load_model(MODEL_PATH)
    return _model


def preprocess_image(img_path):
    img = Image.open(img_path).convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


def predict_disease(img_path):
    """
    Runs inference on a single image file path.
    Returns (class_label: str, confidence_percent: float).
    """
    model = get_model()
    arr = preprocess_image(img_path)
    preds = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(preds))
    confidence = round(float(preds[idx]) * 100, 2)
    label = CLASS_NAMES[idx]
    return label, confidence