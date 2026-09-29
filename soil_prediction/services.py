def generate_soil_report(data):
    ph = data["ph"]

    if ph < 5.5:
        ph_status = "Acidic screening result"
        ph_message = (
            "The entered pH is acidic. Confirm it with a soil laboratory "
            "and ask for crop-specific lime or soil-amendment guidance."
        )
        ph_level = "attention"

    elif ph <= 7.5:
        ph_status = "Near-neutral screening range"
        ph_message = (
            "The entered pH is within a broad near-neutral screening range. "
            "Crop-specific suitability still depends on the crop and local soil conditions."
        )
        ph_level = "normal"

    else:
        ph_status = "Alkaline screening result"
        ph_message = (
            "The entered pH is alkaline. Confirm the result and request "
            "crop-specific guidance from a soil laboratory or agriculture officer."
        )
        ph_level = "attention"

    recommendations = [
        "Keep the original soil-test report and record the sampling date and field location.",
        "Use the laboratory's units and test method when interpreting N, P and K values.",
        "Do not apply fertilizer or soil amendments solely from this screening report.",
        "For a crop-specific nutrient plan, consult a local soil-testing laboratory or agriculture officer.",
    ]

    if not data.get("organic_carbon"):
        recommendations.append(
            "Consider including organic carbon in your next soil test."
        )

    if not data.get("electrical_conductivity"):
        recommendations.append(
            "Consider testing electrical conductivity (EC) if salinity is a concern."
        )

    return {
        "title": "Soil screening report",
        "ph_status": ph_status,
        "ph_message": ph_message,
        "ph_level": ph_level,
        "nutrients": {
            "Nitrogen (N)": data["nitrogen"],
            "Phosphorus (P)": data["phosphorus"],
            "Potassium (K)": data["potassium"],
        },
        "recommendations": recommendations,
        "disclaimer": (
            "This is an informational screening report, not a laboratory diagnosis "
            "or fertilizer prescription. Nutrient interpretation depends on units, "
            "soil-test method, crop, soil type and local conditions."
        ),
    }