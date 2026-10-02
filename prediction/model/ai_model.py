"""
Compatibility wrapper for prediction.ai_model.
Ensures any legacy imports referencing prediction.model.ai_model
utilize the optimized, thread-safe TensorFlow inference pipeline.
"""
from prediction.ai_model import (
    CANDIDATE_CLASS_PATHS,
    CANDIDATE_MODEL_PATHS,
    DEFAULT_CLASS_NAMES,
    find_class_names_path,
    find_model_path,
    get_class_names,
    get_model,
    load_class_names,
    load_crop_model,
    predict_disease,
)

__all__ = [
    "predict_disease",
    "get_model",
    "get_class_names",
    "load_crop_model",
    "load_class_names",
    "DEFAULT_CLASS_NAMES",
    "CANDIDATE_MODEL_PATHS",
    "CANDIDATE_CLASS_PATHS",
    "find_model_path",
    "find_class_names_path",
]