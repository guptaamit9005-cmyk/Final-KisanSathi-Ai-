from pathlib import Path
from PIL import Image


# ============================================================
# AGRIVISION AI - MULTI-DISEASE DEMO PREDICTOR
# ============================================================


DISEASE_DATA = {

    # ========================================================
    # RICE
    # ========================================================

    "Rice": {

        "Healthy": {
            "confidence": 96.4,

            "organic_treatment":
                "No disease treatment is required. "
                "Maintain healthy soil and proper irrigation.",

            "chemical_treatment":
                "No chemical treatment is required "
                "for a healthy crop.",

            "fertilizer":
                "Use balanced NPK fertilizer according "
                "to soil-test recommendations.",

            "prevention":
                "Use healthy seeds, maintain proper spacing, "
                "monitor the crop regularly and maintain "
                "balanced irrigation.",
        },


        "Leaf Blast": {
            "confidence": 94.2,

            "organic_treatment":
                "Remove severely infected leaves and "
                "maintain good field sanitation. "
                "Avoid excessive nitrogen fertilizer.",

            "chemical_treatment":
                "Use an appropriate fungicide according "
                "to the product label and local agricultural "
                "recommendations.",

            "fertilizer":
                "Maintain balanced nitrogen, phosphorus "
                "and potassium application. Avoid excessive "
                "nitrogen fertilizer.",

            "prevention":
                "Use healthy disease-free seeds, maintain "
                "proper plant spacing, monitor leaves regularly "
                "and remove infected plant material.",
        },


        "Brown Spot": {
            "confidence": 92.7,

            "organic_treatment":
                "Remove heavily affected leaves and maintain "
                "good field sanitation. Improve crop nutrition "
                "and avoid prolonged leaf wetness.",

            "chemical_treatment":
                "Use an appropriate fungicide according to "
                "local agricultural recommendations and "
                "product-label instructions.",

            "fertilizer":
                "Maintain balanced nutrition, especially "
                "adequate potassium and other nutrients "
                "based on soil requirements.",

            "prevention":
                "Use healthy seeds, maintain balanced "
                "fertilization, improve field sanitation "
                "and monitor the crop regularly.",
        },
    },


    # ========================================================
    # TOMATO
    # ========================================================

    "Tomato": {

        "Healthy": {
            "confidence": 97.1,

            "organic_treatment":
                "No disease treatment is required. "
                "Continue normal crop-care practices.",

            "chemical_treatment":
                "No chemical treatment is required "
                "for a healthy plant.",

            "fertilizer":
                "Use balanced fertilizer according "
                "to soil-test and crop requirements.",

            "prevention":
                "Maintain proper irrigation, good airflow, "
                "regular monitoring and remove damaged "
                "plant material.",
        },


        "Early Blight": {
            "confidence": 93.5,

            "organic_treatment":
                "Remove affected leaves, improve airflow "
                "around plants and avoid overhead watering.",

            "chemical_treatment":
                "Use an appropriate fungicide according "
                "to local agricultural guidance and "
                "product-label instructions.",

            "fertilizer":
                "Maintain balanced plant nutrition and "
                "avoid excessive nitrogen application.",

            "prevention":
                "Maintain good spacing, avoid prolonged "
                "leaf wetness, remove infected leaves and "
                "keep the growing area clean.",
        },


        "Late Blight": {
            "confidence": 95.3,

            "organic_treatment":
                "Remove and safely dispose of severely "
                "infected plant material. Improve airflow "
                "and avoid unnecessary leaf wetness.",

            "chemical_treatment":
                "Use an appropriate fungicide according "
                "to local agricultural recommendations "
                "and product-label instructions.",

            "fertilizer":
                "Maintain balanced nutrition and avoid "
                "excessive nitrogen that can encourage "
                "lush susceptible growth.",

            "prevention":
                "Maintain good airflow, avoid overhead "
                "irrigation, monitor plants frequently "
                "and remove infected material promptly.",
        },
    },
}


# ============================================================
# DEMO PREDICTION
# ============================================================

def analyze_image(image_path, crop="Rice", disease=None):

    """
    Presentation/demo prediction engine.

    IMPORTANT:
    This is NOT a trained machine-learning model.

    It validates the uploaded image and returns
    predefined demonstration results.
    """

    image_path = Path(image_path)


    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    # --------------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------------

    try:

        with Image.open(image_path) as image:

            image.verify()

    except Exception as error:

        raise ValueError(
            f"Invalid image file: {error}"
        )


    # --------------------------------------------------------
    # CHECK CROP
    # --------------------------------------------------------

    if crop not in DISEASE_DATA:

        crop = "Rice"


    available_diseases = DISEASE_DATA[crop]


    # --------------------------------------------------------
    # SELECT DISEASE
    # --------------------------------------------------------

    if disease not in available_diseases:

        disease = list(
            available_diseases.keys()
        )[1]


    data = available_diseases[disease]


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {

        "crop": crop,

        "disease_name": disease,

        "confidence": data["confidence"],

        "organic_treatment":
            data["organic_treatment"],

        "chemical_treatment":
            data["chemical_treatment"],

        "fertilizer":
            data["fertilizer"],

        "prevention":
            data["prevention"],
    }