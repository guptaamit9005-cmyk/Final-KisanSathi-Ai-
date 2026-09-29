import random

from PIL import Image


# ============================================================
# KISANSATHI AI
# DISEASE-SPECIFIC ADVISORY DATABASE
# ============================================================

DISEASE_DATABASE = {

    # ========================================================
    # RICE - BROWN SPOT
    # ========================================================

    "Rice Brown Spot": {
        "crop": "Rice",
        "type": "Disease Detected",

        "cause": (
            "Brown spot is a fungal disease that can be associated "
            "with crop stress and nutrient imbalance."
        ),

        "solution": [
            "Remove and manage severely affected plant material.",
            "Maintain proper field sanitation.",
            "Maintain balanced crop nutrition.",
            "Avoid prolonged crop stress.",
            "Monitor the crop regularly for new brown lesions."
        ],

        "treatment": [
            "Follow locally recommended disease-management practices.",
            "Use plant-protection products only according to "
            "the current label and local agricultural advice."
        ],

        "fertilizer": {
            "name": "Balanced NPK fertilizer",
            "recommendation": (
                "Apply NPK according to soil-test results and "
                "the rice crop stage."
            ),
            "special": (
                "If zinc deficiency is confirmed, use a zinc "
                "source according to local soil-test guidance."
            )
        }
    },


    # ========================================================
    # RICE - LEAF BLAST
    # ========================================================

    "Rice Leaf Blast": {
        "crop": "Rice",
        "type": "Disease Detected",

        "cause": (
            "Rice blast is a fungal disease that can affect "
            "leaves and, under suitable conditions, panicles."
        ),

        "solution": [
            "Monitor the crop regularly for expanding blast lesions.",
            "Maintain balanced nitrogen management.",
            "Avoid excessive nitrogen application.",
            "Maintain appropriate field management.",
            "Follow locally recommended blast-management practices."
        ],

        "treatment": [
            "For significant disease pressure, follow the "
            "current local blast-management recommendation.",
            "Do not apply fungicides without checking the "
            "current product label and local advice."
        ],

        "fertilizer": {
            "name": "Balanced NPK + need-based nitrogen",
            "recommendation": (
                "Apply nitrogen according to soil test and "
                "crop stage rather than applying excess nitrogen."
            ),
            "special": (
                "Balanced nutrient management is preferred; "
                "avoid unnecessary excessive nitrogen."
            )
        }
    },


    # ========================================================
    # TOMATO - EARLY BLIGHT
    # ========================================================

    "Tomato Early Blight": {
        "crop": "Tomato",
        "type": "Disease Detected",

        "cause": (
            "Early blight is a fungal disease commonly affecting "
            "tomato foliage and potentially fruit."
        ),

        "solution": [
            "Remove severely affected leaves.",
            "Maintain adequate spacing between plants.",
            "Improve air circulation around the crop.",
            "Avoid prolonged leaf wetness.",
            "Remove diseased plant debris.",
            "Monitor newly developing leaves regularly."
        ],

        "treatment": [
            "Follow the current local early-blight management advisory.",
            "For chemical treatment, use only a locally approved "
            "product at its label-recommended rate."
        ],

        "fertilizer": {
            "name": "Tomato NPK 100:50:50 kg/ha + FYM 10 t/ha",
            "recommendation": (
                "Use this as the prototype reference recommendation "
                "for tomato nutrition."
            ),
            "special": (
                "Actual fertilizer quantities should be adjusted "
                "according to soil test, variety and crop stage."
            )
        }
    },


    # ========================================================
    # TOMATO - LATE BLIGHT
    # ========================================================

    "Tomato Late Blight": {
        "crop": "Tomato",
        "type": "Disease Detected",

        "cause": (
            "Late blight is a serious tomato disease that can "
            "spread rapidly under favorable environmental conditions."
        ),

        "solution": [
            "Remove severely affected plant material.",
            "Improve air circulation around plants.",
            "Avoid unnecessary leaf wetness.",
            "Maintain appropriate plant spacing.",
            "Monitor the crop frequently.",
            "Remove diseased debris from the field."
        ],

        "treatment": [
            "Follow the current local late-blight management advisory.",
            "Use only locally approved plant-protection products "
            "according to their current label."
        ],

        "fertilizer": {
            "name": "Tomato NPK 100:50:50 kg/ha + FYM 10 t/ha",
            "recommendation": (
                "Maintain balanced tomato nutrition rather than "
                "using excessive nitrogen."
            ),
            "special": (
                "Adjust the actual fertilizer program according "
                "to soil test and crop stage."
            )
        }
    },


    # ========================================================
    # RICE - HEALTHY
    # ========================================================

    "Rice Healthy": {
        "crop": "Rice",
        "type": "Healthy Crop",

        "cause": (
            "No disease is identified by this prototype result."
        ),

        "solution": [
            "Continue regular crop monitoring.",
            "Maintain proper irrigation management.",
            "Maintain field sanitation.",
            "Monitor for early disease symptoms.",
            "Maintain balanced crop nutrition."
        ],

        "treatment": [
            "No disease treatment is recommended from this "
            "prototype healthy result."
        ],

        "fertilizer": {
            "name": "Soil-test-based balanced NPK",
            "recommendation": (
                "Apply nutrients according to soil-test results "
                "and rice crop stage."
            ),
            "special": (
                "Use micronutrients such as zinc when deficiency "
                "is established."
            )
        }
    },


    # ========================================================
    # TOMATO - HEALTHY
    # ========================================================

    "Tomato Healthy": {
        "crop": "Tomato",
        "type": "Healthy Crop",

        "cause": (
            "No disease is identified by this prototype result."
        ),

        "solution": [
            "Continue regular crop monitoring.",
            "Maintain proper plant spacing.",
            "Maintain good field hygiene.",
            "Remove damaged or diseased leaves when necessary.",
            "Monitor plants during flowering and fruiting."
        ],

        "treatment": [
            "No disease treatment is recommended from this "
            "prototype healthy result."
        ],

        "fertilizer": {
            "name": "Tomato NPK 100:50:50 kg/ha + FYM 10 t/ha",
            "recommendation": (
                "Use this as the prototype reference for tomato "
                "nutrient management."
            ),
            "special": (
                "Adjust fertilizer according to soil test, "
                "crop stage and local agricultural advice."
            )
        }
    }
}


# ============================================================
# DISEASE PREDICTION
# ============================================================

def predict_disease(image_path):

    # --------------------------------------------------------
    # OPEN IMAGE
    # --------------------------------------------------------

    try:

        image = Image.open(image_path).convert("RGB")

    except Exception as e:

        raise ValueError(
            f"Unable to read uploaded image: {e}"
        )


    # --------------------------------------------------------
    # BASIC IMAGE VALIDATION
    # --------------------------------------------------------

    if image.width < 50 or image.height < 50:

        raise ValueError(
            "Image is too small for crop analysis."
        )


    # --------------------------------------------------------
    # PROTOTYPE PREDICTION
    #
    # IMPORTANT:
    # This is temporary demo classification.
    # Replace this block with the trained ML model later.
    # --------------------------------------------------------

    disease_name = random.choice(
        list(DISEASE_DATABASE.keys())
    )


    # --------------------------------------------------------
    # DEMO CONFIDENCE
    # --------------------------------------------------------

    confidence = random.choice([
        88.4,
        89.7,
        91.2,
        92.6,
        94.1,
        95.3
    ])


    # --------------------------------------------------------
    # GET DISEASE DATA
    # --------------------------------------------------------

    disease_data = DISEASE_DATABASE[disease_name]

    fertilizer_data = disease_data["fertilizer"]


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "disease": disease_name,

        "disease_name": disease_name,

        "crop": disease_data["crop"],

        "type": disease_data["type"],

        "cause": disease_data["cause"],

        "confidence": confidence,

        "solution": disease_data["solution"],

        "treatment": disease_data["treatment"],

        "fertilizer": fertilizer_data["name"],

        "fertilizer_recommendation": (
            fertilizer_data["recommendation"]
        ),

        "fertilizer_special": (
            fertilizer_data["special"]
        ),

        "prototype": True,
    }