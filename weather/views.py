import requests

from collections import defaultdict
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


OPENWEATHER_CURRENT_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
)

OPENWEATHER_FORECAST_URL = (
    "https://api.openweathermap.org/data/2.5/forecast"
)


@login_required(login_url="accounts:login")
def weather_home(request):
    return render(request, "weather/weather.html")


def _get_weather_api_key():
    return getattr(settings, "OPENWEATHER_API_KEY", "").strip()


def _get_json(url, params):
    """
    Calls OpenWeatherMap and returns its JSON response.
    Raises requests exceptions for network/API failures.
    """
    response = requests.get(url, params=params, timeout=15)

    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.status_code != 200:
        message = data.get("message", "Weather service request failed.")
        raise ValueError(message)

    return data


def _map_om_code(code):
    if code == 0: return "Clear sky"
    elif code in [1, 2, 3]: return "Partly cloudy"
    elif code in [45, 48]: return "Fog"
    elif code in [51, 53, 55]: return "Drizzle"
    elif code in [56, 57]: return "Freezing Drizzle"
    elif code in [61, 63, 65]: return "Rain"
    elif code in [66, 67]: return "Freezing Rain"
    elif code in [71, 73, 75]: return "Snow fall"
    elif code == 77: return "Snow grains"
    elif code in [80, 81, 82]: return "Rain showers"
    elif code in [85, 86]: return "Snow showers"
    elif code in [95, 96, 99]: return "Thunderstorm"
    return "Unknown"


def _build_forecast_summary(om_data):
    """
    Advanced 7-day agro-meteorological forecast from Open-Meteo.
    """
    planner = []
    times = om_data.get("time", [])
    max_temps = om_data.get("temperature_2m_max", [])
    min_temps = om_data.get("temperature_2m_min", [])
    precips = om_data.get("precipitation_sum", [])
    precip_probs = om_data.get("precipitation_probability_max", [])
    wind_speeds = om_data.get("wind_speed_10m_max", [])
    codes = om_data.get("weather_code", [])

    for i in range(len(times)):
        try:
            planner.append({
                "date": times[i],
                "min_temp": round(min_temps[i], 1) if min_temps[i] is not None else None,
                "max_temp": round(max_temps[i], 1) if max_temps[i] is not None else None,
                "rain_probability": precip_probs[i] if precip_probs[i] is not None else 0,
                "rainfall_mm": round(precips[i], 1) if precips[i] is not None else 0,
                "max_wind_kmh": round(wind_speeds[i], 1) if wind_speeds[i] is not None else None,
                "description": _map_om_code(codes[i]) if codes[i] is not None else "Forecast unavailable",
            })
        except IndexError:
            break

    return planner[:7]


def _calculate_dew_point(temp_c, humidity):
    """Magnus formula approximation for dew point temperature (°C)."""
    if temp_c is None or humidity is None or humidity <= 0:
        return None
    import math
    a = 17.27
    b = 237.7
    try:
        alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        return round(dew_point, 1)
    except (ValueError, ZeroDivisionError):
        return None


def _calculate_gdd(t_max, t_min, base_temp=10.0):
    """Calculate Growing Degree Days (GDD) with base temperature."""
    if t_max is None or t_min is None:
        return 0.0
    mean_temp = (t_max + t_min) / 2.0
    gdd = max(0.0, mean_temp - base_temp)
    return round(gdd, 1)


def _build_farming_advice(weather, planner, crop, crop_stage, irrigation_type, soil_type):
    """
    Advanced Agri-Weather Intelligence Engine:
    Evaluates microclimate parameters against crop physiological needs and field operations:
    1. Operational Windows: Spraying, Sowing/Harvesting, Fertilizing
    2. Disease & Pest Risk Matrix (Fungal, Blight, Sucking Pests)
    3. Smart Irrigation Decision & Soil Evaporation Budget
    4. Active Agronomic Watch Alerts & AI Operational Summary
    """
    advice = []
    alerts = []

    temperature = weather.get("temperature", 25.0)
    feels_like = weather.get("feels_like", temperature)
    humidity = weather.get("humidity", 50)
    wind_kmh = weather.get("wind_speed_kmh", 8.0)
    current_rain = weather.get("rainfall", 0) or 0
    pressure = weather.get("pressure", 1013)

    next_day = planner[0] if planner else {}
    next_rain_prob = next_day.get("rain_probability", 0) or 0
    next_rainfall_mm = next_day.get("rainfall_mm", 0) or 0
    max_next_wind = next_day.get("max_wind_kmh", wind_kmh) or wind_kmh

    # 3-day and 5-day aggregated outlook
    total_5d_rain = sum(d.get("rainfall_mm", 0) for d in planner) if planner else 0
    max_5d_temp = max((d.get("max_temp") for d in planner if d.get("max_temp") is not None), default=temperature)
    min_5d_temp = min((d.get("min_temp") for d in planner if d.get("min_temp") is not None), default=temperature)

    dew_point = _calculate_dew_point(temperature, humidity)
    crop_name = crop.strip().title() if crop else "General Crops"
    stage_name = (crop_stage or "vegetative").replace("_", " ").title()
    soil_name = (soil_type or "alluvial").replace("_", " ").title()
    irr_name = (irrigation_type or "Drip").title()

    # -------------------------------------------------------------
    # 1. SPRAYING INTELLIGENCE WINDOW
    # -------------------------------------------------------------
    spray_score = 100
    spray_reasons = []

    if wind_kmh >= 20:
        spray_score -= 50
        spray_reasons.append(f"High wind drift risk ({wind_kmh} km/h - target is < 15 km/h)")
    elif wind_kmh >= 14:
        spray_score -= 20
        spray_reasons.append(f"Moderate wind speed ({wind_kmh} km/h) - exercise caution with drift")
    elif wind_kmh < 4:
        spray_score -= 10
        spray_reasons.append("Air inversion possible in calm air (< 4 km/h)")

    if current_rain > 0:
        spray_score -= 70
        spray_reasons.append("Active rain washes off chemical deposits immediately")
    elif next_rain_prob >= 60 or next_rainfall_mm >= 3:
        spray_score -= 40
        spray_reasons.append(f"Imminent rain within 24h ({next_rain_prob}% prob, {next_rainfall_mm} mm)")

    if temperature >= 35:
        spray_score -= 30
        spray_reasons.append(f"High temperature ({temperature}°C) induces droplet evaporation and leaf scorch")
    elif temperature < 10:
        spray_score -= 20
        spray_reasons.append("Low temperature retards systemic chemical uptake")

    if humidity < 35:
        spray_score -= 15
        spray_reasons.append(f"Low relative humidity ({humidity}%) accelerates droplet evaporation")

    spray_score = max(0, min(100, spray_score))
    if spray_score >= 80:
        spray_status = "Optimal"
        spray_badge = "success"
        spray_verdict = "Excellent conditions for foliar nutrient and pest spray application."
    elif spray_score >= 50:
        spray_status = "Marginal"
        spray_badge = "warning"
        spray_verdict = "Sub-optimal window. Spray early morning or late afternoon when wind subsides."
    else:
        spray_status = "Unfavorable"
        spray_badge = "danger"
        spray_verdict = "Spray strictly not recommended due to droplet drift, wash-off, or rapid vaporization."

    # -------------------------------------------------------------
    # 2. FIELD WORKABILITY & HARVEST / SOWING READINESS
    # -------------------------------------------------------------
    workability_score = 100
    work_notes = []

    if current_rain > 0 or total_5d_rain > 25:
        workability_score -= 60
        work_notes.append("Soil is waterlogged/wet; tractor machinery movement causes compaction.")
    elif next_rain_prob > 50:
        workability_score -= 25
        work_notes.append(f"Approaching precipitation ({next_rain_prob}% prob) may disrupt harvest drying.")
    
    if temperature > 40:
        workability_score -= 30
        work_notes.append("Severe heat stress for field operators and draft animals between 11 AM - 4 PM.")

    workability_score = max(0, min(100, workability_score))
    if workability_score >= 75:
        workability_status = "Excellent"
        workability_badge = "success"
    elif workability_score >= 45:
        workability_status = "Moderate"
        workability_badge = "warning"
    else:
        workability_status = "Poor / Delayed"
        workability_badge = "danger"

    # -------------------------------------------------------------
    # 3. DISEASE & PEST MICROCLIMATE RISK
    # -------------------------------------------------------------
    # Fungal pathogens thrive in high humidity (>75%) + warm temps (20-30°C) + leaf wetness
    fungal_index = 0
    fungal_factors = []
    if humidity >= 78:
        fungal_index += 45
        fungal_factors.append(f"Sustained ambient humidity ({humidity}%) creates prolonged leaf wetness")
    elif humidity >= 65:
        fungal_index += 20

    if 20 <= temperature <= 31:
        fungal_index += 35
        fungal_factors.append(f"Temperature {temperature}°C is in the prime reproduction zone for blast/rust/blight spores")
    
    if next_rain_prob >= 50 or current_rain > 0:
        fungal_index += 20
        fungal_factors.append("Rain splash and humidity spikes favor secondary pathogen spread")

    fungal_index = min(100, fungal_index)
    if fungal_index >= 70:
        fungal_risk = "High Risk"
        fungal_badge = "danger"
        fungal_recom = f"High alert for fungal/bacterial leaf spot, downy mildew, and blast in {crop_name}. Scout lower canopy and apply bio-fungicide preventative measures."
    elif fungal_index >= 40:
        fungal_risk = "Moderate Watch"
        fungal_badge = "warning"
        fungal_recom = f"Moderate risk of spore germination. Ensure field perimeter weed clearance and adequate aeration between rows."
    else:
        fungal_risk = "Low Risk"
        fungal_badge = "success"
        fungal_recom = f"Microclimate is clean and unfavorable for foliar fungal development."

    # Sucking pest pressure (aphids, thrips, whiteflies favor dry, warm conditions)
    pest_pressure = "Normal"
    pest_badge = "info"
    if temperature >= 28 and humidity <= 50 and wind_kmh <= 12:
        pest_pressure = "Elevated"
        pest_badge = "warning"
        pest_tip = f"Dry & warm conditions favor sucking pests (thrips, aphids, mites) on young {crop_name} shoots. Place yellow/blue sticky traps."
    else:
        pest_tip = "Pest proliferation indices are within standard seasonal baseline."

    # -------------------------------------------------------------
    # 4. SMART IRRIGATION ADVISORY & WATER BUDGETING
    # -------------------------------------------------------------
    # Evapotranspiration estimate (Simplified Hargreaves/pan approximation mm/day)
    base_et0 = 3.5
    if temperature > 35:
        base_et0 += 2.5
    elif temperature > 28:
        base_et0 += 1.5
    elif temperature < 18:
        base_et0 -= 1.0

    if humidity < 40:
        base_et0 += 1.2
    elif humidity > 75:
        base_et0 -= 1.2

    if wind_kmh > 15:
        base_et0 += 0.8

    estimated_et0 = max(1.5, round(base_et0, 1))

    # Irrigation recommendation
    if current_rain >= 10 or next_rainfall_mm >= 15 or next_rain_prob >= 75:
        irr_action = "Hold Irrigation (Rain Sufficient)"
        irr_code = "hold"
        irr_badge = "success"
        irr_reason = f"Upcoming forecast indicates significant rainfall ({next_rainfall_mm} mm expected, {next_rain_prob}% probability). Natural precipitation covers root-zone moisture needs."
        water_saving_tip = f"Saves ~{round(estimated_et0 * 10, 0)} mm water cycle and diesel/electricity pumping costs."
    elif next_rain_prob >= 50 or next_rainfall_mm >= 5:
        irr_action = "Postpone & Monitor Field"
        irr_code = "postpone"
        irr_badge = "warning"
        irr_reason = f"Rain probability is {next_rain_prob}% with {next_rainfall_mm} mm possible tomorrow. Check soil moisture probe before initiating full irrigation cycle."
        water_saving_tip = "Avoid waterlogging, especially in clay or heavy black soils."
    elif irr_name == "Rainfed":
        irr_action = "Rainfed Crop - Conserve Soil Moisture"
        irr_code = "rainfed"
        irr_badge = "info"
        irr_reason = f"Field is configured as rainfed. With ET loss at ~{estimated_et0} mm/day, maintain surface mulching to conserve moisture in {soil_name} soil."
        water_saving_tip = "Apply organic mulch or shallow intercultural hoeing to break capillary loss."
    else:
        irr_action = "Irrigate As Per Schedule"
        irr_code = "irrigate"
        irr_badge = "primary"
        irr_reason = f"Clear/dry outlook with daily crop evapotranspiration loss of ~{estimated_et0} mm/day. Provide scheduled watering for {crop_name} ({stage_name} stage)."
        water_saving_tip = f"Best watering window: Early morning (5-8 AM) or late evening (5-7 PM) using {irr_name} to minimize evaporative loss."

    # VPD (Vapour Pressure Deficit) kPa — crop transpiration stress metric
    import math
    vpd_kpa = None
    try:
        if temperature is not None and humidity is not None and humidity > 0:
            svp = 0.6108 * math.exp((17.27 * temperature) / (temperature + 237.3))
            vpd_kpa = round(svp * (1 - humidity / 100.0), 2)
    except (ValueError, ZeroDivisionError):
        pass

    # GDD — using today's forecast first-day max/min if available
    gdd_today = None
    if planner:
        first_day = planner[0]
        t_max = first_day.get("max_temp")
        t_min = first_day.get("min_temp")
        gdd_today = _calculate_gdd(t_max, t_min, base_temp=10.0)

    # Determine irrigation_need score (0-100, inverse of hold probability)
    irrigation_need = 0
    if irr_code == "irrigate":
        irrigation_need = 90
    elif irr_code == "postpone":
        irrigation_need = 55
    elif irr_code == "rainfed":
        irrigation_need = 40
    else:  # hold
        irrigation_need = 15

    intelligence = {
        "overall_health_score": round((spray_score * 0.35) + (workability_score * 0.35) + ((100 - fungal_index) * 0.3)),

        # Flat shortcut keys used by the JS dashboard
        "spray_score":       spray_score,
        "spray_status":      spray_status,
        "spray_badge":       spray_badge,
        "workability_score": workability_score,
        "workability_status": workability_status,
        "fungal_index":      fungal_index,
        "fungal_risk":       fungal_risk,
        "irrigation_need":   irrigation_need,
        "irr_badge":         irr_badge,
        "irr_action":        irr_action,
        "dew_point":         dew_point,
        "vpd_kpa":           vpd_kpa,
        "gdd_today":         gdd_today,
        "est_et0":           estimated_et0,

        # Nested detail blocks (available for advanced UI components)
        "spray_window": {
            "score": spray_score,
            "status": spray_status,
            "badge": spray_badge,
            "verdict": spray_verdict,
            "reasons": spray_reasons if spray_reasons else ["Wind speed, temperature and rain indicators are within ideal operational envelope."]
        },
        "field_workability": {
            "score": workability_score,
            "status": workability_status,
            "badge": workability_badge,
            "notes": work_notes if work_notes else ["Ideal soil and thermal conditions for tillage, weeding, or field work."]
        },
        "disease_risk": {
            "score": fungal_index,
            "status": fungal_risk,
            "badge": fungal_badge,
            "recommendation": fungal_recom,
            "factors": fungal_factors if fungal_factors else ["Microclimate is unfavorable for rapid foliar fungal development."]
        },
        "pest_pressure": {
            "level": pest_pressure,
            "badge": pest_badge,
            "tip": pest_tip
        },
        "irrigation_decision": {
            "action": irr_action,
            "code": irr_code,
            "badge": irr_badge,
            "reason": irr_reason,
            "water_saving_tip": water_saving_tip,
            "daily_et_mm": estimated_et0
        }
    }

    # Add actionable advisory cards for UI
    advice.append({
        "type": "spraying",
        "status": "good" if spray_score >= 80 else ("caution" if spray_score >= 50 else "warning"),
        "title": f"Foliar Spray Advisory: {spray_status} ({spray_score}/100)",
        "reason": spray_verdict,
        "action": spray_reasons[0] if spray_reasons else "Ideal window for applying micronutrients, bio-stimulants, or crop protection."
    })

    advice.append({
        "type": "irrigation",
        "status": "good" if irr_code == "hold" else ("caution" if irr_code == "postpone" else "info"),
        "title": f"Irrigation Command: {irr_action}",
        "reason": irr_reason,
        "action": water_saving_tip
    })

    advice.append({
        "type": "disease",
        "status": "warning" if fungal_index >= 70 else ("caution" if fungal_index >= 40 else "good"),
        "title": f"Pathogen & Crop Stress: {fungal_risk}",
        "reason": fungal_recom,
        "action": f"Recommended for {crop_name} in {stage_name} stage: scout underside of leaves for early symptom detection."
    })

    advice.append({
        "type": "fieldwork",
        "status": "good" if workability_score >= 75 else ("caution" if workability_score >= 45 else "warning"),
        "title": f"Field Machinery & Labor Window: {workability_status}",
        "reason": " ".join(work_notes) if work_notes else "Soil traction and weather are optimal for mechanized field passes.",
        "action": f"Soil type '{soil_name}' holds good workability window under current moisture dynamics."
    })

    # 5. ACTIONABLE AGRICULTURAL DECISION MATRIX ("Karna Chahiye Ki Nahi")
    decisions = []

    # A. Irrigation (सिंचाई)
    if irr_code == "hold":
        dec_irr = {
            "id": "irrigation",
            "title_hi": "सिंचाई (Irrigation)",
            "icon": "🚿",
            "action": "DONT",
            "badge": "🛑 आज सिंचाई रोकें (Hold)",
            "badge_class": "badge-danger",
            "verdict": irr_reason,
            "tip": water_saving_tip,
        }
    elif irr_code == "postpone":
        dec_irr = {
            "id": "irrigation",
            "title_hi": "सिंचाई (Irrigation)",
            "icon": "🚿",
            "action": "CAUTION",
            "badge": "⚠️ पहले नमी जांचें (Check)",
            "badge_class": "badge-warning",
            "verdict": irr_reason,
            "tip": water_saving_tip,
        }
    else:
        dec_irr = {
            "id": "irrigation",
            "title_hi": "सिंचाई (Irrigation)",
            "icon": "🚿",
            "action": "DO",
            "badge": "✅ आज सिंचाई करें (Recommended)",
            "badge_class": "badge-success",
            "verdict": irr_reason,
            "tip": water_saving_tip,
        }
    decisions.append(dec_irr)

    # B. Spraying (छिड़काव)
    if spray_score >= 75:
        dec_spray = {
            "id": "spraying",
            "title_hi": "दवा/कीटनाशक छिड़काव (Spraying)",
            "icon": "🧪",
            "action": "DO",
            "badge": "✅ छिड़काव के लिए उत्तम (Optimal)",
            "badge_class": "badge-success",
            "verdict": spray_verdict,
            "tip": f"हवा की गति {wind_kmh} km/h अनुकूल है। सुबह 7-10 या शाम 4-6 बजे छिड़काव करें।",
        }
    elif spray_score >= 45:
        dec_spray = {
            "id": "spraying",
            "title_hi": "दवा/कीटनाशक छिड़काव (Spraying)",
            "icon": "🧪",
            "action": "CAUTION",
            "badge": "⚠️ सावधानी से करें (Caution)",
            "badge_class": "badge-warning",
            "verdict": spray_verdict,
            "tip": "हवा शांत होने पर ही नोजल पौधे के करीब रखकर स्प्रे करें।",
        }
    else:
        dec_spray = {
            "id": "spraying",
            "title_hi": "दवा/कीटनाशक छिड़काव (Spraying)",
            "icon": "🧪",
            "action": "DONT",
            "badge": "🛑 आज छिड़काव न करें (Avoid)",
            "badge_class": "badge-danger",
            "verdict": spray_verdict,
            "tip": (spray_reasons[0] if spray_reasons else "दवा बहने या वाष्पीकृत होने से नुकसान होगा।"),
        }
    decisions.append(dec_spray)

    # C. Fertilizer / Urea (उर्वरक/खाद प्रयोग)
    if next_rain_prob >= 65 or next_rainfall_mm >= 15 or current_rain > 0:
        dec_fert = {
            "id": "fertilizer",
            "title_hi": "उर्वरक व खाद प्रयोग (Fertilizing)",
            "icon": "🌾",
            "action": "DONT",
            "badge": "🛑 अभी यूरिया/खाद न डालें (Avoid)",
            "badge_class": "badge-danger",
            "verdict": f"आगामी वर्षा ({next_rainfall_mm} mm / {next_rain_prob}%) से खाद बहकर खेत से बाहर चली जाएगी (Leaching Risk)।",
            "tip": "बारिश रुकने और जल निकासी के बाद ही टॉप ड्रेसिंग करें।",
        }
    elif temperature >= 38:
        dec_fert = {
            "id": "fertilizer",
            "title_hi": "उर्वरक व खाद प्रयोग (Fertilizing)",
            "icon": "🌾",
            "action": "CAUTION",
            "badge": "⚠️ सिंचाई के साथ ही दें (With Irrigation)",
            "badge_class": "badge-warning",
            "verdict": f"अधिक तापमान ({temperature}°C) में सूखी मिट्टी पर यूरिया डालने से पौधों की जड़ें व पत्तियां जल सकती हैं।",
            "tip": "शाम के समय सिंचाई के साथ अथवा हल्की नमी में ही प्रयोग करें।",
        }
    else:
        dec_fert = {
            "id": "fertilizer",
            "title_hi": "उर्वरक व खाद प्रयोग (Fertilizing)",
            "icon": "🌾",
            "action": "DO",
            "badge": "✅ खाद डाल सकते हैं (Safe)",
            "badge_class": "badge-success",
            "verdict": f"मौसम स्थिर है और तापमान {temperature}°C पोषक तत्वों के अवशोषण के लिए अनुकूल है।",
            "tip": f"{crop_name} की {stage_name} अवस्था अनुसार अनुशंसित मात्रा में ही उर्वरक दें।",
        }
    decisions.append(dec_fert)

    # D. Harvesting & Drying (कटाई व गहाई)
    if next_rain_prob >= 50 or next_rainfall_mm >= 5 or total_5d_rain >= 15:
        dec_harv = {
            "id": "harvesting",
            "title_hi": "फसल कटाई व गहाई (Harvesting)",
            "icon": "✂️",
            "action": "DONT",
            "badge": "🛑 कटाई रोकें / तिरपाल रखें (Rain Alert)",
            "badge_class": "badge-danger",
            "verdict": f"संभावित वर्षा ({next_rain_prob}% संभावना) से कटी फसल में दाना अंकुरित होने व फफूंद का खतरा है।",
            "tip": "कटे हुए अनाज और भूसे को तुरंत सुरक्षित शेड या तिरपाल से ढक कर रखें।",
        }
    elif humidity >= 80:
        dec_harv = {
            "id": "harvesting",
            "title_hi": "फसल कटाई व गहाई (Harvesting)",
            "icon": "✂️",
            "action": "CAUTION",
            "badge": "⚠️ दोपहर में ही गहाई करें (Wait for Sun)",
            "badge_class": "badge-warning",
            "verdict": f"सुबह उच्च आर्द्रता ({humidity}%) के कारण दानों में नमी अधिक रहेगी।",
            "tip": "धूप निकलने और ओस सूखने के बाद 11 बजे से 4 बजे के बीच थ्रेशिंग करें।",
        }
    else:
        dec_harv = {
            "id": "harvesting",
            "title_hi": "फसल कटाई व गहाई (Harvesting)",
            "icon": "✂️",
            "action": "DO",
            "badge": "✅ कटाई के लिए उत्तम मौसम (Clear)",
            "badge_class": "badge-success",
            "verdict": "धूप खिली रहेगी और मौसम सूखा है। फसल कटाई, सुखाने और भंडारण के लिए आदर्श समय।",
            "tip": "अनाज को 12% से कम नमी स्तर तक सुखाकर ही भंडारण करें।",
        }
    decisions.append(dec_harv)

    # E. Tillage & Sowing (जुताई व बुवाई)
    if current_rain > 0 or total_5d_rain > 30:
        dec_till = {
            "id": "tillage",
            "title_hi": "जुताई एवं बुवाई (Tillage & Sowing)",
            "icon": "🚜",
            "action": "DONT",
            "badge": "🛑 भारी जुताई रोकें (Soil Too Wet)",
            "badge_class": "badge-danger",
            "verdict": "खेत में अत्यधिक नमी है। ट्रैक्टर या हल चलाने से मिट्टी की संरचना खराब होगी और ढेले बनेंगे।",
            "tip": "खेत में 'बतर' (ओट) आने की प्रतीक्षा करें।",
        }
    elif workability_score >= 70:
        dec_till = {
            "id": "tillage",
            "title_hi": "जुताई एवं बुवाई (Tillage & Sowing)",
            "icon": "🚜",
            "action": "DO",
            "badge": "✅ जुताई/बुवाई के लिए अनुकूल (Optimal)",
            "badge_class": "badge-success",
            "verdict": f"{soil_name} मिट्टी में जुताई और बीज बुवाई के लिए उत्तम ट्रैक्टर ग्रिप और नमी संतुलन है।",
            "tip": "बीजोपचार (Seed treatment) करके ही बुवाई करें ताकि भूमि जनित रोगों से सुरक्षा मिले।",
        }
    else:
        dec_till = {
            "id": "tillage",
            "title_hi": "जुताई एवं बुवाई (Tillage & Sowing)",
            "icon": "🚜",
            "action": "CAUTION",
            "badge": "⚠️ हल्की जुताई ही करें (Moderate)",
            "badge_class": "badge-warning",
            "verdict": "मिट्टी में नमी का स्तर मध्यम है।",
            "tip": "गहरी जुताई के स्थान पर कल्टीवेटर या हैरो का प्रयोग करें।",
        }
    decisions.append(dec_till)

    intelligence["decisions"] = decisions

    # Alert triggers
    if temperature >= 38:
        alerts.append({
            "level": "danger",
            "title": "Severe Heat Stress Alert",
            "message": f"Extreme daytime temperature of {temperature}°C forecast. Apply light frequent irrigation or anti-transpirants to prevent flower drop and pollen sterility."
        })
    elif temperature <= 4:
        alerts.append({
            "level": "danger",
            "title": "Frost / Low Temperature Watch",
            "message": f"Temperature dropping to {temperature}°C. Risk of frost injury. Create night-time field smoke (thath) or light flood irrigation to regulate canopy temperature."
        })

    if wind_kmh >= 30:
        alerts.append({
            "level": "warning",
            "title": "High Wind Squall Alert",
            "message": f"Wind gusts reach {wind_kmh} km/h. High lodging risk in tall standing crops (sugarcane, maize, lodging wheat). Ensure support staking."
        })

    if next_rain_prob >= 75 or next_rainfall_mm >= 20:
        alerts.append({
            "level": "warning",
            "title": "Heavy Precipitation Warning",
            "message": f"High probability ({next_rain_prob}%) of intense rain ({next_rainfall_mm} mm) in the next 24-48 hours. Clear drainage channels to prevent water stagnation."
        })

    if not alerts:
        alerts.append({
            "level": "safe",
            "title": "Stable Microclimate Conditions",
            "message": f"No extreme meteorological events detected for {weather.get('city')}. Favorable agricultural operations window."
        })

    return {
        "advice": advice,
        "alerts": alerts,
        "intelligence": intelligence
    }


def _fetch_openmeteo_live(lat=None, lon=None, city=None):
    """
    Direct high-accuracy live meteorological data from Open-Meteo.
    Geocodes city name automatically if coords are not provided.
    """
    resolved_name = city or "Current Location"
    country_name = "India"

    # 1. Geocode city if lat/lon not provided
    if (lat is None or lon is None or lat == "" or lon == "") and city:
        try:
            geo_resp = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "en"},
                timeout=8
            )
            if geo_resp.status_code == 200:
                results = geo_resp.json().get("results", [])
                if results:
                    lat = results[0].get("latitude")
                    lon = results[0].get("longitude")
                    resolved_name = results[0].get("name", city)
                    country_name = results[0].get("country", country_name)
        except Exception:
            pass

    if lat is None or lon is None or lat == "" or lon == "":
        raise ValueError(f"Could not locate '{city}'. Please check spelling or click 'Auto-Detect Location'.")

    # 2. Fetch current and 7-day daily forecast in a single API call
    om_resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": float(lat),
            "longitude": float(lon),
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,surface_pressure,wind_speed_10m,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "timezone": "auto"
        },
        timeout=12
    )

    if om_resp.status_code != 200:
        raise ValueError("Live meteorological data service is currently unavailable.")

    data = om_resp.json()
    curr = data.get("current", {})
    daily = data.get("daily", {})

    temp_c = curr.get("temperature_2m", 25.0)
    feels_c = curr.get("apparent_temperature", temp_c)
    humidity = curr.get("relative_humidity_2m", 50)
    wind_kmh = curr.get("wind_speed_10m", 8.0)
    pressure = curr.get("surface_pressure", 1013)
    precip_mm = curr.get("precipitation", 0.0)
    w_code = curr.get("weather_code", 0)
    desc = _map_om_code(w_code)

    weather = {
        "city": resolved_name,
        "country": country_name,
        "temperature": round(temp_c, 1),
        "feels_like": round(feels_c, 1),
        "humidity": int(humidity),
        "pressure": round(pressure, 1),
        "wind_speed": round(wind_kmh / 3.6, 1),  # m/s for legacy frontend
        "wind_speed_kmh": round(wind_kmh, 1),
        "rainfall": round(precip_mm, 1),
        "description": desc,
        "icon": "",
        "lat": lat,
        "lon": lon,
    }

    forecast = _build_forecast_summary(daily)
    return weather, forecast, lat, lon


@login_required(login_url="accounts:login")
def weather_api(request):
    city = request.GET.get("city", "").strip()

    # GPS coordinates — passed when the user clicks "Auto-Detect".
    lat = request.GET.get("lat", "").strip()
    lon = request.GET.get("lon", "").strip()

    # Optional farm context supplied by the frontend.
    crop = request.GET.get("crop", "").strip()
    crop_stage = request.GET.get("crop_stage", "").strip()
    soil_type = request.GET.get("soil_type", "").strip()
    irrigation_type = request.GET.get("irrigation_type", "").strip()

    if not city and (not lat or not lon):
        return JsonResponse({
            "success": False,
            "message": "Please enter your city or allow location access."
        }, status=400)

    weather = None
    forecast = []
    forecast_error = None
    api_lat = lat
    api_lon = lon

    api_key = _get_weather_api_key()

    # Try OpenWeatherMap first if key is present
    if api_key:
        try:
            if lat and lon:
                owm_params = {
                    "lat": float(lat),
                    "lon": float(lon),
                    "appid": api_key,
                    "units": "metric",
                }
            else:
                owm_params = {
                    "q": city,
                    "appid": api_key,
                    "units": "metric",
                }

            current_data = _get_json(OPENWEATHER_CURRENT_URL, owm_params)
            weather_item = (current_data.get("weather") or [{}])[0]
            wind_speed_ms = current_data.get("wind", {}).get("speed", 0)

            weather = {
                "city": current_data.get("name", city),
                "country": current_data.get("sys", {}).get("country", ""),
                "temperature": round(current_data.get("main", {}).get("temp", 0), 1),
                "feels_like": round(current_data.get("main", {}).get("feels_like", 0), 1),
                "humidity": current_data.get("main", {}).get("humidity", 0),
                "pressure": current_data.get("main", {}).get("pressure", 0),
                "wind_speed": wind_speed_ms,
                "wind_speed_kmh": round(wind_speed_ms * 3.6, 1),
                "rainfall": current_data.get("rain", {}).get("1h", 0),
                "description": weather_item.get("description", "").title(),
                "icon": weather_item.get("icon", ""),
            }

            api_lat = lat or current_data.get("coord", {}).get("lat")
            api_lon = lon or current_data.get("coord", {}).get("lon")

        except Exception:
            weather = None

    # If OpenWeatherMap failed or was unavailable, use Open-Meteo live API!
    if not weather:
        try:
            weather, forecast, api_lat, api_lon = _fetch_openmeteo_live(lat=lat, lon=lon, city=city)
        except ValueError as err:
            return JsonResponse({"success": False, "message": str(err)}, status=400)
        except Exception:
            return JsonResponse({
                "success": False,
                "message": "Live weather service is temporarily unavailable. Please try again."
            }, status=503)

    # If forecast was not fetched yet, fetch 7-day forecast via Open-Meteo using coords
    if not forecast and api_lat and api_lon:
        try:
            om_url = "https://api.open-meteo.com/v1/forecast"
            om_params = {
                "latitude": float(api_lat),
                "longitude": float(api_lon),
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
                "timezone": "auto"
            }
            om_resp = requests.get(om_url, params=om_params, timeout=12)
            if om_resp.status_code == 200:
                om_data = om_resp.json().get("daily", {})
                forecast = _build_forecast_summary(om_data)
        except Exception:
            forecast_error = "7-day forecast temporarily unavailable."

    # 3. Compute Agricultural Intelligence & Do's / Don'ts Decision Matrix
    farming = _build_farming_advice(
        weather=weather,
        planner=forecast,
        crop=crop,
        crop_stage=crop_stage,
        irrigation_type=irrigation_type,
        soil_type=soil_type,
    )

    return JsonResponse({
        "success": True,
        "weather": weather,
        "forecast": forecast,
        "farm_advice": farming["advice"],
        "alerts": farming["alerts"],
        "intelligence": farming["intelligence"],
        "decisions": farming["intelligence"].get("decisions", []),
        "profile": {
            "city": weather.get("city", city),
            "crop": crop,
            "crop_stage": crop_stage,
            "soil_type": soil_type,
            "irrigation_type": irrigation_type,
        },
        "forecast_error": forecast_error,
        "advisory_disclaimer": (
            "Weather-based planning guidance only. It is not a confirmed "
            "crop diagnosis or a guaranteed safe-operation recommendation. "
            "Check field conditions, product labels and local expert advice."
        ),
    })