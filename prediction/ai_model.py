import gc
import json
import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================
# TENSORFLOW MEMORY & CPU OPTIMIZATIONS FOR LOW-RESOURCE HOSTS
# Must be set before TensorFlow initializes to restrict thread
# pools and disable unneeded background allocations (Render 512MB RAM)
# ============================================================
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "1")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Project root:
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Candidate paths for the trained model
CANDIDATE_MODEL_PATHS = [
    PROJECT_ROOT / "prediction" / "model" / "crop_disease_model.keras",
    PROJECT_ROOT / "model_training" / "artifacts" / "crop_disease_model.keras",
    PROJECT_ROOT / "prediction" / "ml_models" / "crop_disease_model.keras",
]

# Candidate paths for class names JSON
CANDIDATE_CLASS_PATHS = [
    PROJECT_ROOT / "prediction" / "model" / "class_names.json",
    PROJECT_ROOT / "model_training" / "artifacts" / "class_names.json",
]

# Exact 16 classes matched to crop_disease_model.keras output layer
DEFAULT_CLASS_NAMES = [
    "Cashew healthy",
    "Cashew leaf miner",
    "Cashew red rust",
    "Fungi",
    "Healthy",
    "Maize healthy",
    "Maize leaf blight",
    "Maize streak virus",
    "Nematode",
    "Tomato healthy",
    "Tomato septoria leaf spot",
    "Tomato verticulium wilt",
    "bacterial_leaf_blight",
    "brown_spot",
    "leaf_blast",
    "rice_healthy",
]

# Thread-safe singletons
_model = None
_model_lock = threading.Lock()
_class_names = None
_class_names_lock = threading.Lock()


def find_model_path() -> Optional[Path]:
    """Find the first existing, non-empty model file from candidate paths."""
    for path in CANDIDATE_MODEL_PATHS:
        if path.exists() and path.stat().st_size > 0:
            return path
    return None


def find_class_names_path() -> Optional[Path]:
    """Find the first existing class names JSON file from candidate paths."""
    for path in CANDIDATE_CLASS_PATHS:
        if path.exists() and path.stat().st_size > 0:
            return path
    return None


def get_model():
    """
    Thread-safe singleton loader for the TensorFlow crop disease model.
    Loads the model once per worker process with compile=False and single-thread CPU limits
    to prevent memory exhaustion (SIGKILL) on Render.
    """
    global _model

    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model

        model_path = find_model_path()
        if model_path is None:
            searched = [str(p) for p in CANDIDATE_MODEL_PATHS]
            raise FileNotFoundError(
                f"Trained crop disease model (.keras) not found. Searched locations: {searched}"
            )

        logger.info("Model loading started from %s (compile=False for memory efficiency)...", model_path)

        import tensorflow as tf

        # Configure CPU threading limits within TensorFlow
        try:
            tf.config.threading.set_intra_op_parallelism_threads(1)
            tf.config.threading.set_inter_op_parallelism_threads(1)
        except RuntimeError:
            pass

        # compile=False avoids loading optimizer state and building backward-pass graphs
        _model = tf.keras.models.load_model(str(model_path), compile=False)

        input_shape = getattr(_model, "input_shape", None)
        output_shape = getattr(_model, "output_shape", None)
        logger.info(
            "Model loading completed successfully. Input shape: %s, Output shape: %s",
            input_shape,
            output_shape,
        )

        return _model


def get_class_names() -> List[str]:
    """
    Thread-safe loader for disease classification class names.
    Supports JSON list, JSON dict, and falls back to DEFAULT_CLASS_NAMES.
    """
    global _class_names

    if _class_names is not None:
        return _class_names

    with _class_names_lock:
        if _class_names is not None:
            return _class_names

        class_path = find_class_names_path()
        if class_path is not None:
            try:
                with open(class_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, dict):
                    try:
                        classes = [
                            data[str(i)] if str(i) in data else data[i]
                            for i in range(len(data))
                        ]
                    except (KeyError, TypeError):
                        classes = list(data.values())
                elif isinstance(data, list):
                    classes = [str(x) for x in data]
                else:
                    classes = []

                if classes:
                    _class_names = classes
                    logger.info("Loaded %d class names from %s", len(_class_names), class_path)
                    return _class_names
            except Exception as err:
                logger.warning("Failed to parse class names from %s: %s. Using default classes.", class_path, err)

        _class_names = list(DEFAULT_CLASS_NAMES)
        logger.info("Using default 16 class names list (%d classes)", len(_class_names))
        return _class_names


# Backward-compatible alias functions
def load_crop_model():
    return get_model()


def load_class_names():
    return get_class_names()


def _parse_crop_and_disease(class_label: str) -> Tuple[str, str]:
    """
    Parse a class label into normalized crop name and disease name.
    """
    raw = str(class_label or "").strip()
    norm = raw.lower().replace("_", " ").strip()

    # Exact mappings for the trained 16 classes
    EXACT_MAP = {
        "cashew healthy": ("Cashew", "Healthy"),
        "cashew leaf miner": ("Cashew", "Leaf Miner"),
        "cashew red rust": ("Cashew", "Red Rust"),
        "fungi": ("", "Fungi"),
        "healthy": ("", "Healthy"),
        "maize healthy": ("Maize", "Healthy"),
        "maize leaf blight": ("Maize", "Leaf Blight"),
        "maize streak virus": ("Maize", "Streak Virus"),
        "nematode": ("", "Nematode"),
        "tomato healthy": ("Tomato", "Healthy"),
        "tomato septoria leaf spot": ("Tomato", "Septoria Leaf Spot"),
        "tomato verticulium wilt": ("Tomato", "Verticillium Wilt"),
        "bacterial leaf blight": ("Rice", "Bacterial Leaf Blight"),
        "brown spot": ("Rice", "Brown Spot"),
        "leaf blast": ("Rice", "Leaf Blast"),
        "rice healthy": ("Rice", "Healthy"),
    }

    if norm in EXACT_MAP:
        return EXACT_MAP[norm]

    # Heuristic prefix parsing for any custom or extended labels
    for crop in ["cashew", "tomato", "maize", "rice", "potato", "apple", "grape", "wheat"]:
        if norm.startswith(crop):
            remainder = norm[len(crop):].strip()
            disease_part = remainder if remainder else "Healthy"
            return crop.title(), disease_part.title()

    return "", raw.title()


def predict_disease(image_path: Any) -> Dict[str, Any]:
    """
    Perform memory-efficient disease prediction from an uploaded leaf image.

    Workflow:
    1. Validate image path exists.
    2. Retrieve singleton model and class names.
    3. Load image with PIL, resize to model input dimensions (160x160).
    4. Run direct model callable inference (avoids tf.data memory pipeline).
    5. Parse class probabilities, top predictions, crop name, and severity.
    6. Collect garbage and return structured results.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Uploaded crop image not found: {image_path}")

    logger.info("Prediction started for image: %s", image_path.name)

    model = get_model()
    class_names = get_class_names()

    # Determine input dimensions expected by the trained model (defaults to 160x160)
    input_shape = getattr(model, "input_shape", None)
    if input_shape and len(input_shape) >= 3 and input_shape[1] and input_shape[2]:
        image_height = int(input_shape[1])
        image_width = int(input_shape[2])
    else:
        image_height = 160
        image_width = 160

    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img = img.resize((image_width, image_height))
            # Model includes internal preprocessing layer (mobilenet_v2.preprocess_input),
            # so raw [0, 255] float32 pixels are expected
            image_array = np.asarray(img, dtype=np.float32)
    except UnidentifiedImageError as err:
        logger.warning("Uploaded file is not a valid image: %s", err)
        raise ValueError("Uploaded file is not a valid image. Please upload a clear JPG, PNG, or WebP photo.") from err

    image_array = np.expand_dims(image_array, axis=0)
    logger.info("Image preprocessing completed. Shape: %s, Dtype: %s", image_array.shape, image_array.dtype)

    # Direct execution avoids model.predict() dataset pipeline overhead
    predictions = model(image_array, training=False)
    if hasattr(predictions, "numpy"):
        predictions = predictions.numpy()

    probabilities = np.asarray(predictions)[0]

    if len(probabilities) != len(class_names):
        logger.warning(
            "Model returned %d classes, but class_names has %d.",
            len(probabilities),
            len(class_names),
        )
        if len(probabilities) == len(DEFAULT_CLASS_NAMES):
            class_names = DEFAULT_CLASS_NAMES
        else:
            raise ValueError(
                f"Model output dimension ({len(probabilities)}) does not match class list ({len(class_names)})."
            )

    predicted_index = int(np.argmax(probabilities))
    confidence_val = float(probabilities[predicted_index]) * 100.0

    raw_label = class_names[predicted_index]
    parsed_crop, parsed_disease = _parse_crop_and_disease(raw_label)

    # Top 3 predictions
    top_indices = np.argsort(probabilities)[::-1][:3]
    top_predictions = []
    for idx in top_indices:
        lbl = class_names[int(idx)]
        c_p, d_p = _parse_crop_and_disease(lbl)
        conf = float(probabilities[idx]) * 100.0
        top_predictions.append({
            "full_label": lbl,
            "crop_name": c_p,
            "crop": c_p,
            "disease_name": d_p,
            "disease": d_p,
            "confidence": round(conf, 2),
        })

    # Severity classification
    is_healthy = ("healthy" in parsed_disease.lower()) or ("healthy" in raw_label.lower())
    if is_healthy:
        severity = "Healthy"
    elif confidence_val >= 80.0:
        severity = "High"
    elif confidence_val >= 55.0:
        severity = "Medium"
    else:
        severity = "Low"

    # Explicit garbage collection to release intermediate arrays
    gc.collect()

    logger.info(
        "Prediction completed successfully. Disease: '%s', Crop: '%s', Confidence: %.2f%%, Severity: %s",
        parsed_disease,
        parsed_crop,
        confidence_val,
        severity,
    )

    return {
        "full_label": raw_label,
        "crop_name": parsed_crop,
        "crop": parsed_crop,
        "disease_name": parsed_disease,
        "disease": parsed_disease,
        "confidence": f"{confidence_val:.2f}%",
        "confidence_value": round(confidence_val, 2),
        "severity": severity,
        "top_predictions": top_predictions,
    }