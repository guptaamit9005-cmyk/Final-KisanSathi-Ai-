"""
Maps the raw class label the model outputs to everything the UI needs to
show: a readable name, health status, severity, spread risk, and a
treatment plan (organic + chemical where relevant).

The keys below match the standard PlantVillage dataset folder/class names.
If you train on a different dataset, update CLASS_NAMES in predictor.py
and the keys here to match, in the same order.
"""

DISEASE_INFO = {

    "Pepper__bell___Bacterial_spot": {
        "name": "Bell Pepper — Bacterial Spot",
        "status": "infected",
        "severity": "Moderate",
        "spread": "High",
        "treatment": [
            "Remove and destroy infected leaves and fruit immediately",
            "Apply a copper-based bactericide every 7–10 days",
            "Avoid overhead watering; water at the base only",
            "Rotate crops — don't replant peppers/tomatoes in the same soil for 2 years",
        ],
    },
    "Pepper__bell___healthy": {
        "name": "Bell Pepper — Healthy",
        "status": "healthy",
        "severity": "None",
        "spread": "Low",
        "treatment": [
            "No treatment needed",
            "Maintain consistent watering and full sun exposure",
            "Re-scan every 1–2 weeks during growing season",
        ],
    },

    "Potato___Early_blight": {
        "name": "Potato — Early Blight",
        "status": "infected",
        "severity": "Moderate",
        "spread": "Medium",
        "treatment": [
            "Remove lower, older leaves showing dark concentric spots",
            "Apply a chlorothalonil or copper-based fungicide",
            "Improve airflow by spacing plants further apart",
            "Mulch soil to reduce spore splash from rain",
        ],
    },
    "Potato___Late_blight": {
        "name": "Potato — Late Blight",
        "status": "infected",
        "severity": "Severe",
        "spread": "High",
        "treatment": [
            "Isolate and destroy affected plants — this spreads fast",
            "Apply a systemic fungicide containing mancozeb or metalaxyl",
            "Avoid working in the field when foliage is wet",
            "Consult a local agronomist if spread continues after treatment",
        ],
    },
    "Potato___healthy": {
        "name": "Potato — Healthy",
        "status": "healthy",
        "severity": "None",
        "spread": "Low",
        "treatment": [
            "No treatment needed",
            "Maintain regular hilling and consistent moisture",
            "Re-scan every 1–2 weeks during growing season",
        ],
    },

    "Tomato_Bacterial_spot": {
        "name": "Tomato — Bacterial Spot",
        "status": "infected",
        "severity": "Moderate",
        "spread": "High",
        "treatment": [
            "Remove and destroy infected leaves",
            "Apply copper-based bactericide weekly",
            "Disinfect pruning tools between plants",
            "Avoid handling plants when foliage is wet",
        ],
    },
    "Tomato_Early_blight": {
        "name": "Tomato — Early Blight",
        "status": "infected",
        "severity": "Moderate",
        "spread": "Medium",
        "treatment": [
            "Prune affected lower leaves",
            "Apply a copper or chlorothalonil-based fungicide",
            "Stake plants to improve air circulation",
            "Rotate with non-solanaceous crops next season",
        ],
    },
    "Tomato_Late_blight": {
        "name": "Tomato — Late Blight",
        "status": "infected",
        "severity": "Severe",
        "spread": "High",
        "treatment": [
            "Remove and destroy infected plants immediately",
            "Apply a systemic fungicide (metalaxyl or mancozeb-based)",
            "Avoid overhead irrigation entirely",
            "Consult a local agronomist — this can wipe out a field fast",
        ],
    },
    "Tomato_Leaf_Mold": {
        "name": "Tomato — Leaf Mold",
        "status": "infected",
        "severity": "Mild",
        "spread": "Medium",
        "treatment": [
            "Increase greenhouse/field ventilation to lower humidity",
            "Apply a sulfur-based or copper fungicide",
            "Remove and destroy affected leaves",
            "Avoid wetting foliage during watering",
        ],
    },
    "Tomato_healthy": {
        "name": "Tomato — Healthy",
        "status": "healthy",
        "severity": "None",
        "spread": "Low",
        "treatment": [
            "No treatment needed",
            "Maintain regular watering and balanced fertilizer",
            "Re-scan every 1–2 weeks during growing season",
        ],
    },
}