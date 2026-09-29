import os
import numpy as np
from PIL import Image

try:
    import tensorflow as tf
except ImportError:
    tf = None


MODEL = None

LABELS = []


def load_model():

    global MODEL
    global LABELS

    if tf is None:
        return

    if MODEL is None:

        model_path = os.path.join(
            os.path.dirname(__file__),
            "model",
            "crop_model.keras"
        )

        labels_path = os.path.join(
            os.path.dirname(__file__),
            "labels.txt"
        )

        MODEL = tf.keras.models.load_model(model_path)

        with open(labels_path, "r") as f:
            LABELS = [line.strip() for line in f.readlines()]


def preprocess(image_path):

    image = Image.open(image_path)

    image = image.convert("RGB")

    image = image.resize((224, 224))

    image = np.array(image)

    image = image / 255.0

    image = np.expand_dims(image, axis=0)

    return image


def predict(image_path):

    if tf is None:

        return {

            "crop_name": "Unknown",

            "prediction": "TensorFlow Not Installed",

            "confidence": 0,

            "organic": "Install TensorFlow first.",

            "chemical": "-",

            "fertilizer": "-",

            "prevention": "-"

        }

    load_model()

    image = preprocess(image_path)

    predictions = MODEL.predict(image)

    confidence = float(np.max(predictions)) * 100

    index = int(np.argmax(predictions))

    disease = LABELS[index]

    return {

        "crop_name": disease.split("___")[0],

        "prediction": disease,

        "confidence": round(confidence, 2),

        "organic": "Neem oil spray every 7 days.",

        "chemical": "Apply recommended fungicide according to agricultural guidelines.",

        "fertilizer": "Balanced NPK fertilizer.",

        "prevention": "Remove infected leaves and avoid overwatering."

    }