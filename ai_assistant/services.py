def get_ai_response(question):

    question_lower = question.lower()

    # Disease / crop health
    if any(
        word in question_lower
        for word in [
            "disease",
            "disease",
            "बीमारी",
            "रोग",
            "leaf",
            "पत्ता",
            "spots",
            "दाग"
        ]
    ):

        return (
            "🌿 KisanSathi सुझाव:\n\n"
            "अगर फसल की पत्तियों पर दाग, पीलापन या सूखापन दिखाई दे रहा है, "
            "तो पहले Crop Health Analysis में अपनी फसल और symptoms select करें। "
            "साथ में अपने क्षेत्र का weather data भी check करें।\n\n"
            "अगर symptoms बढ़ रहे हैं, तो स्थानीय कृषि विशेषज्ञ से पुष्टि "
            "करवाना बेहतर रहेगा।"
        )

    # Weather
    if any(
        word in question_lower
        for word in [
            "weather",
            "temperature",
            "rain",
            "बारिश",
            "मौसम",
            "तापमान"
        ]
    ):

        return (
            "🌦️ KisanSathi Weather:\n\n"
            "अपने क्षेत्र का current temperature, humidity और rainfall "
            "देखने के लिए Weather section खोलें।\n\n"
            "मौसम के आधार पर irrigation और crop-health decisions लेने से "
            "पहले local conditions भी ध्यान में रखें।"
        )

    # Irrigation
    if any(
        word in question_lower
        for word in [
            "water",
            "irrigation",
            "पानी",
            "सिंचाई"
        ]
    ):

        return (
            "💧 Irrigation Advice:\n\n"
            "सिंचाई का निर्णय crop, growth stage, soil condition और "
            "recent rainfall को ध्यान में रखकर लें।\n\n"
            "बहुत अधिक पानी देने से root-related problems और fungal "
            "diseases का risk बढ़ सकता है।"
        )

    # Farming learning
    if any(
        word in question_lower
        for word in [
            "learn",
            "learning",
            "farming",
            "खेती",
            "कृषि",
            "सीखना"
        ]
    ):

        return (
            "📚 KisanSathi Farming Learning:\n\n"
            "आप crop selection, seed management, irrigation, "
            "crop diseases, fertilizers, harvesting और market-related "
            "topics सीख सकते हैं।\n\n"
            "KisanSathi के Learning section में topic-wise information "
            "देखें।"
        )

    # Default response
    return (
        "👨‍🌾 Namaste! Main KisanSathi AI hoon.\n\n"
        "Aap mujhse farming ke baare mein pooch sakte hain, jaise:\n\n"
        "🌱 Crop disease\n"
        "🌦️ Weather\n"
        "💧 Irrigation\n"
        "🌾 Crop management\n"
        "📚 Farming learning\n\n"
        "Example: 'Mere tomato ke patton par brown spots hain, kya karu?'"
    )