import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError


# Project root:
# AgriVisionAi-main/AgriVisionAi-main/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ARTIFACTS_DIR = PROJECT_ROOT / "model_training" / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "crop_disease_model.keras"
CLASS_NAMES_PATH = ARTIFACTS_DIR / "class_names.json"


@lru_cache(maxsize=1)
def load_crop_model():
    """
    Load the trained model once and reuse it for later predictions.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained crop model not found: {MODEL_PATH}"
        )

    return tf.keras.models.load_model(MODEL_PATH)


@lru_cache(maxsize=1)
def load_class_names():
    """
    Load class labels saved during training.
    Supports either a JSON list or a dictionary.
    """
    if not CLASS_NAMES_PATH.exists():
        raise FileNotFoundError(
            f"Class labels file not found: {CLASS_NAMES_PATH}"
        )

    with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as file:
        class_names = json.load(file)

    if isinstance(class_names, dict):
        # Convert {"0": "class_a", "1": "class_b"} to ordered list.
        try:
            class_names = [
                class_names[str(index)]
                if str(index) in class_names
                else class_names[index]
                for index in range(len(class_names))
            ]
        except (KeyError, TypeError):
            class_names = list(class_names.values())

    if not isinstance(class_names, list) or not class_names:
        raise ValueError(
            "class_names.json must contain a non-empty list or dictionary."
        )

    return [str(name) for name in class_names]


def predict_disease(image_path):
    """
    Predict crop disease from an uploaded image.

    Returns a dictionary compatible with prediction/views.py:
    {
        "disease_name": "...",
        "confidence": "99.06%",
        "top_predictions": [...]
    }
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Uploaded crop image not found: {image_path}"
        )

    try:
        model = load_crop_model()
        class_names = load_class_names()

        # Read expected image dimensions from the trained model.
        input_shape = model.input_shape

        image_height = input_shape[1] or 160
        image_width = input_shape[2] or 160

        # Load and resize uploaded image.
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image = image.resize((image_width, image_height))

            image_array = np.asarray(image, dtype=np.float32)

        image_array = np.expand_dims(image_array, axis=0)

        # The trained model includes its preprocessing layer.
        predictions = model.predict(image_array, verbose=0)[0]

        if len(predictions) != len(class_names):
            raise ValueError(
                "Model output count does not match class_names.json. "
                f"Model outputs: {len(predictions)}, "
                f"class labels: {len(class_names)}."
            )

        top_indices = np.argsort(predictions)[::-1][:3]

        top_predictions = []

        for index in top_indices:
            top_predictions.append({
                "disease_name": class_names[int(index)],
                "confidence": round(float(predictions[index]) * 100, 2),
            })

        best_prediction = top_predictions[0]

        return {
            "disease_name": best_prediction["disease_name"],
            "confidence": f'{best_prediction["confidence"]:.2f}%',
            "top_predictions": top_predictions,
        }

    except UnidentifiedImageError as error:
        raise ValueError(
            "Uploaded file is not a valid image. Please upload JPG or PNG."
        ) from error