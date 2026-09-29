# prediction/rule_engine.py


DISEASE_DATABASE = {

    "rice": [
        {
            "disease": "Rice Brown Spot",
            "symptoms": ["brown_spots", "yellow_leaves"],
            "treatment": (
                "Remove badly affected leaves and maintain proper field nutrition. "
                "Use a suitable fungicide only according to local agricultural guidance."
            ),
            "prevention": (
                "Use healthy seeds, maintain balanced fertilization, "
                "and avoid prolonged crop stress."
            ),
        },
        {
            "disease": "Rice Leaf Blast",
            "symptoms": ["leaf_blast", "brown_spots"],
            "treatment": (
                "Remove heavily affected plant material and maintain balanced "
                "nitrogen management. Consult a local agriculture expert for "
                "fungicide selection."
            ),
            "prevention": (
                "Use resistant varieties where available, avoid excessive nitrogen, "
                "and maintain proper crop spacing."
            ),
        },
    ],

    "tomato": [
        {
            "disease": "Tomato Early Blight",
            "symptoms": ["brown_spots", "yellow_leaves"],
            "treatment": (
                "Remove severely affected leaves and improve air circulation. "
                "Use an appropriate fungicide according to local recommendations."
            ),
            "prevention": (
                "Avoid overhead irrigation, maintain plant spacing, "
                "remove infected plant debris, and practice crop rotation."
            ),
        },
        {
            "disease": "Tomato Late Blight",
            "symptoms": ["dark_spots", "water_soaked"],
            "treatment": (
                "Remove severely infected plant material and improve ventilation. "
                "Seek local agricultural guidance for suitable disease control."
            ),
            "prevention": (
                "Avoid prolonged leaf wetness, improve airflow, "
                "and monitor crops during cool and humid weather."
            ),
        },
    ],

    "wheat": [
        {
            "disease": "Wheat Rust",
            "symptoms": ["rust", "yellow_leaves"],
            "treatment": (
                "Remove severely affected plant material where practical and "
                "consult local agricultural recommendations for disease control."
            ),
            "prevention": (
                "Use resistant varieties where available and regularly monitor "
                "the crop for rust symptoms."
            ),
        },
    ],

    "potato": [
        {
            "disease": "Potato Leaf Blight Risk",
            "symptoms": ["dark_spots", "water_soaked"],
            "treatment": (
                "Remove severely affected foliage and improve field ventilation. "
                "Consult local agricultural experts for suitable treatment."
            ),
            "prevention": (
                "Avoid excessive leaf wetness and monitor crops carefully "
                "during humid conditions."
            ),
        },
    ],

    "maize": [
        {
            "disease": "Maize Leaf Spot Risk",
            "symptoms": ["brown_spots", "yellow_leaves"],
            "treatment": (
                "Remove severely affected plant material and maintain balanced "
                "crop nutrition."
            ),
            "prevention": (
                "Maintain proper plant spacing, balanced fertilization, "
                "and regular crop monitoring."
            ),
        },
    ],
}


def calculate_environment_score(temperature, humidity):
    """
    Calculates environmental risk contribution.

    Maximum score = 30
    """

    score = 0

    # Humidity contribution
    if humidity >= 80:
        score += 20

    elif humidity >= 65:
        score += 10

    # Temperature contribution
    if 20 <= temperature <= 32:
        score += 10

    return min(score, 30)


def predict_crop_health(
    crop,
    symptoms,
    temperature,
    humidity,
    crop_stage
):
    """
    Image-less crop health prediction.

    Uses:
    - Crop
    - Symptoms
    - Temperature
    - Humidity
    - Crop growth stage
    """

    crop = crop.lower()

    symptoms = set(symptoms)

    diseases = DISEASE_DATABASE.get(crop, [])

    best_match = None
    best_score = 0
    best_match_count = 0

    # -----------------------------------
    # Disease symptom matching
    # -----------------------------------

    for disease in diseases:

        disease_symptoms = set(disease["symptoms"])

        matched_symptoms = symptoms.intersection(disease_symptoms)

        if not disease_symptoms:
            continue

        symptom_score = (
            len(matched_symptoms) / len(disease_symptoms)
        ) * 70

        if symptom_score > best_score:

            best_score = symptom_score
            best_match = disease
            best_match_count = len(matched_symptoms)

    # -----------------------------------
    # Environment score
    # -----------------------------------

    environment_score = calculate_environment_score(
        temperature,
        humidity
    )

    # -----------------------------------
    # Growth stage contribution
    # -----------------------------------

    stage_score = 0

    if crop_stage in ["vegetative", "flowering"]:
        stage_score = 5

    # -----------------------------------
    # Final risk score
    # -----------------------------------

    if best_match and best_match_count > 0:

        risk_score = (
            best_score
            + environment_score
            + stage_score
        )

        risk_score = min(round(risk_score), 95)

        # Severity
        if risk_score >= 75:
            severity = "High"

        elif risk_score >= 50:
            severity = "Medium"

        else:
            severity = "Low"

        return {
            "success": True,
            "disease": best_match["disease"],
            "risk_score": risk_score,
            "severity": severity,
            "treatment": best_match["treatment"],
            "prevention": best_match["prevention"],
            "matched_symptoms": list(
                symptoms.intersection(
                    set(best_match["symptoms"])
                )
            ),
            "environment_score": environment_score,
            "message": (
                "The selected symptoms show a possible disease pattern. "
                "This is a rule-based screening result and should be "
                "confirmed with a local agricultural expert."
            ),
        }

    # -----------------------------------
    # No disease pattern
    # -----------------------------------

    return {
        "success": True,
        "disease": "No strong disease pattern detected",
        "risk_score": 15,
        "severity": "Low",
        "treatment": (
            "Continue regular crop monitoring and maintain proper "
            "irrigation and crop nutrition."
        ),
        "prevention": (
            "Monitor the crop regularly for new symptoms and maintain "
            "good field hygiene."
        ),
        "matched_symptoms": [],
        "environment_score": environment_score,
        "message": (
            "No strong disease pattern was detected from the selected "
            "symptoms. Continue monitoring the crop."
        ),
    }