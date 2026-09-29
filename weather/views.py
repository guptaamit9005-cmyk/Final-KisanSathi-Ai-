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


def _build_forecast_summary(forecast_data):
    """
    OpenWeatherMap free 5-day forecast is generally returned
    in 3-hour intervals. This groups those intervals by date.
    """
    grouped = defaultdict(list)

    for item in forecast_data.get("list", []):
        date_text = item.get("dt_txt", "")

        if not date_text:
            continue

        date_key = date_text.split(" ")[0]
        grouped[date_key].append(item)

    planner = []

    for date_key, entries in grouped.items():
        temperatures = []
        wind_speeds = []
        rain_amounts = []
        rain_probabilities = []
        descriptions = []

        for entry in entries:
            main = entry.get("main", {})
            wind = entry.get("wind", {})
            rain = entry.get("rain", {})
            weather_items = entry.get("weather", [])

            if main.get("temp") is not None:
                temperatures.append(float(main["temp"]))

            if wind.get("speed") is not None:
                # OpenWeatherMap metric wind speed is m/s.
                wind_speeds.append(float(wind["speed"]) * 3.6)

            rain_amounts.append(float(rain.get("3h", 0) or 0))

            if entry.get("pop") is not None:
                rain_probabilities.append(
                    float(entry["pop"]) * 100
                )

            if weather_items:
                descriptions.append(
                    weather_items[0].get("description", "")
                )

        planner.append({
            "date": date_key,
            "min_temp": round(min(temperatures), 1) if temperatures else None,
            "max_temp": round(max(temperatures), 1) if temperatures else None,
            "rain_probability": (
                round(max(rain_probabilities))
                if rain_probabilities else 0
            ),
            "rainfall_mm": round(sum(rain_amounts), 1),
            "max_wind_kmh": (
                round(max(wind_speeds), 1)
                if wind_speeds else None
            ),
            "description": (
                descriptions[0].title()
                if descriptions else "Forecast unavailable"
            ),
        })

    return planner[:5]


def _build_farming_advice(weather, planner, crop, crop_stage, irrigation_type):
    """
    Preliminary weather-screening rules for the UI.
    These are not validated crop-specific agronomy recommendations.
    """
    advice = []
    alerts = []

    temperature = weather.get("temperature")
    humidity = weather.get("humidity")
    wind_kmh = weather.get("wind_speed_kmh")
    current_rainfall = weather.get("rainfall", 0)

    next_day = planner[0] if planner else {}
    next_rain_probability = next_day.get("rain_probability", 0)
    next_rainfall = next_day.get("rainfall_mm", 0)

    crop_label = crop or "your crop"
    stage_label = (crop_stage or "current").replace("_", " ")

    # Irrigation guidance
    if next_rain_probability >= 60 or next_rainfall >= 5:
        advice.append({
            "type": "irrigation",
            "status": "caution",
            "title": "Review irrigation before watering",
            "reason": (
                f"Rain is forecast for the next forecast day "
                f"({next_rain_probability}% probability, "
                f"{next_rainfall} mm forecast rainfall)."
            ),
            "action": (
                "Check field moisture and local rainfall before irrigation. "
                "Do not irrigate automatically from forecast data alone."
            ),
        })
    elif irrigation_type == "Rainfed":
        advice.append({
            "type": "irrigation",
            "status": "info",
            "title": "Monitor rainfall and soil moisture",
            "reason": f"{crop_label} is marked as rainfed.",
            "action": (
                f"Monitor field moisture during the {stage_label} stage "
                "and review updated rainfall forecasts."
            ),
        })
    else:
        advice.append({
            "type": "irrigation",
            "status": "info",
            "title": "Check field moisture",
            "reason": "Weather forecasts do not measure moisture inside your field.",
            "action": (
                "Use field observation or a soil-moisture sensor, crop stage "
                "and local agricultural guidance before deciding irrigation."
            ),
        })

    # Spray-condition screening
    spray_cautions = []

    if current_rainfall and current_rainfall > 0:
        spray_cautions.append("rainfall is currently reported")

    if wind_kmh is not None and wind_kmh >= 15:
        spray_cautions.append(
            f"wind speed is around {wind_kmh} km/h"
        )

    if temperature is not None and temperature >= 35:
        spray_cautions.append(
            f"temperature is around {temperature}°C"
        )

    if next_rain_probability >= 60:
        spray_cautions.append(
            f"forecast rain probability is {next_rain_probability}%"
        )

    if spray_cautions:
        advice.append({
            "type": "spraying",
            "status": "caution",
            "title": "Review spraying conditions",
            "reason": "; ".join(spray_cautions) + ".",
            "action": (
                "Review the product label, updated local forecast and "
                "agricultural expert guidance before spraying."
            ),
        })
    else:
        advice.append({
            "type": "spraying",
            "status": "info",
            "title": "Check conditions before spraying",
            "reason": (
                "The basic weather screening did not identify its "
                "configured caution triggers."
            ),
            "action": (
                "This does not guarantee a safe spray window. Confirm "
                "wind, rain, temperature and product-label instructions."
            ),
        })

    # Weather alerts: these are watch signals, not disease diagnoses.
    if humidity is not None and humidity >= 80:
        alerts.append({
            "level": "warning",
            "title": "High humidity watch",
            "message": (
                f"Humidity is {humidity}%. Inspect {crop_label} for unusual "
                "symptoms and follow local crop-health advisories."
            ),
        })

    if temperature is not None and temperature >= 35:
        alerts.append({
            "level": "warning",
            "title": "High temperature watch",
            "message": (
                f"Temperature is {temperature}°C. Monitor crop stress "
                "and follow local heat-management guidance."
            ),
        })

    if next_rain_probability >= 70:
        alerts.append({
            "level": "warning",
            "title": "Rainfall watch",
            "message": (
                f"Rain probability for the next forecast day is "
                f"{next_rain_probability}%. Review irrigation and outdoor work."
            ),
        })

    if not alerts:
        alerts.append({
            "level": "info",
            "title": "No weather alert triggered",
            "message": (
                "Continue monitoring updated forecasts and actual field conditions."
            ),
        })

    return {
        "advice": advice,
        "alerts": alerts,
    }


@login_required(login_url="accounts:login")
def weather_api(request):
    city = request.GET.get("city", "").strip()

    # Optional farm context supplied by the frontend.
    crop = request.GET.get("crop", "").strip()
    crop_stage = request.GET.get("crop_stage", "").strip()
    soil_type = request.GET.get("soil_type", "").strip()
    irrigation_type = request.GET.get("irrigation_type", "").strip()

    if not city:
        return JsonResponse({
            "success": False,
            "message": "Please enter your city."
        }, status=400)

    api_key = _get_weather_api_key()

    if not api_key:
        return JsonResponse({
            "success": False,
            "message": "Weather API key is not configured."
        }, status=500)

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
    }

    try:
        # 1. Current weather
        current_data = _get_json(
            OPENWEATHER_CURRENT_URL,
            params,
        )

        weather_item = (
            current_data.get("weather") or [{}]
        )[0]

        wind_speed_ms = current_data.get("wind", {}).get("speed", 0)

        weather = {
            "city": current_data.get("name", city),
            "country": current_data.get("sys", {}).get("country", ""),
            "temperature": round(
                current_data.get("main", {}).get("temp", 0), 1
            ),
            "feels_like": round(
                current_data.get("main", {}).get("feels_like", 0), 1
            ),
            "humidity": current_data.get("main", {}).get("humidity", 0),
            "pressure": current_data.get("main", {}).get("pressure", 0),

            # Preserve the old field for existing frontend compatibility.
            "wind_speed": wind_speed_ms,

            # New display-friendly field.
            "wind_speed_kmh": round(wind_speed_ms * 3.6, 1),

            "rainfall": current_data.get("rain", {}).get("1h", 0),
            "description": weather_item.get("description", ""),
            "icon": weather_item.get("icon", ""),
        }

        # 2. Five-day forecast
        forecast = []
        forecast_error = None

        try:
            forecast_data = _get_json(
                OPENWEATHER_FORECAST_URL,
                params,
            )
            forecast = _build_forecast_summary(forecast_data)

        except (requests.RequestException, ValueError):
            # Current weather should still work if forecast fails.
            forecast_error = (
                "Current weather loaded, but forecast is temporarily unavailable."
            )

        # 3. Farming guidance based on the selected context.
        farming = _build_farming_advice(
            weather=weather,
            planner=forecast,
            crop=crop,
            crop_stage=crop_stage,
            irrigation_type=irrigation_type,
        )

        return JsonResponse({
            "success": True,
            "weather": weather,

            # New fields for Weather Intelligence UI.
            "forecast": forecast,
            "farm_advice": farming["advice"],
            "alerts": farming["alerts"],
            "profile": {
                "city": city,
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

    except ValueError as error:
        return JsonResponse({
            "success": False,
            "message": str(error),
        }, status=400)

    except requests.RequestException:
        return JsonResponse({
            "success": False,
            "message": "Weather service is temporarily unavailable."
        }, status=503)

    except (KeyError, TypeError, IndexError):
        return JsonResponse({
            "success": False,
            "message": "Weather data was incomplete or could not be processed."
        }, status=502)