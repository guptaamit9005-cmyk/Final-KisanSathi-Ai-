from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


def home(request):
    return render(request, "core/home.html")


@require_POST
def karran_chat(request):

    message = request.POST.get("message", "").strip().lower()

    if not message:
        return JsonResponse({
            "success": False,
            "reply": "Please ask me something."
        })

    # -----------------------------------------
    # KARRAN RESPONSES
    # -----------------------------------------

    if any(word in message for word in [
        "hello",
        "hi",
        "hey",
        "namaste",
        "नमस्ते"
    ]):

        reply = (
            "Namaste! 🌱 Main Karran hoon, "
            "KisanSathi AI ka farming assistant. "
            "Aap crop disease, weather, farming, "
            "market ya government schemes ke baare mein "
            "mujhse pooch sakte hain."
        )

    elif any(word in message for word in [
        "crop",
        "फसल",
        "disease",
        "बीमारी",
        "रोग"
    ]):

        reply = (
            "Aap apni crop ki clear photo upload karke "
            "Crop Analysis feature use kar sakte hain. "
            "AI possible disease identify karega aur "
            "result expert verification ke liye bheja jayega."
        )

    elif any(word in message for word in [
        "weather",
        "मौसम",
        "बारिश",
        "rain"
    ]):

        reply = (
            "🌦️ KisanSathi AI mein Weather section se "
            "apne city ka current weather check kar sakte hain. "
            "Weather information ke basis par farming guidance "
            "bhi mil sakti hai."
        )

    elif any(word in message for word in [
        "market",
        "mandi",
        "price",
        "भाव",
        "मंडी"
    ]):

        reply = (
            "📈 Aap Mandi section mein crop ke market prices "
            "check kar sakte hain. Crop select karke available "
            "market information dekhi ja sakti hai."
        )

    elif any(word in message for word in [
        "scheme",
        "government",
        "सरकार",
        "योजना",
        "scheme"
    ]):

        reply = (
            "🏛️ KisanSathi AI mein Government Schemes section "
            "mein farmers ke liye available schemes, eligibility "
            "aur application information explore kar sakte hain."
        )

    elif any(word in message for word in [
        "equipment",
        "tractor",
        "machine",
        "ट्रैक्टर",
        "मशीन"
    ]):

        reply = (
            "🚜 KisanSathi AI par farmers agricultural equipment "
            "rent par list aur book kar sakte hain, jaise tractors, "
            "sprayers, harvesters aur seed drills."
        )

    elif any(word in message for word in [
        "land",
        "जमीन",
        "खेत"
    ]):

        reply = (
            "🌾 Land Marketplace ke through available agricultural "
            "land listings explore ki ja sakti hain."
        )

    elif any(word in message for word in [
        "learning",
        "learn",
        "खेती सीखना",
        "सीखना"
    ]):

        reply = (
            "📚 Farmer Learning section mein crop-wise farming "
            "guidance, crop stages aur modern farming practices "
            "seekh sakte hain."
        )

    elif any(word in message for word in [
        "who are you",
        "what are you",
        "tum kaun",
        "आप कौन"
    ]):

        reply = (
            "🤖 Main Karran hoon — KisanSathi AI ka virtual "
            "farming assistant. Main farmers ko farming-related "
            "information aur platform features samajhne mein help "
            "karta hoon."
        )

    else:

        reply = (
            "🌱 Main Karran hoon. Aap mujhse crop disease, "
            "weather, mandi prices, farming learning, equipment, "
            "land ya government schemes ke baare mein pooch sakte hain."
        )

    return JsonResponse({
        "success": True,
        "reply": reply
    })