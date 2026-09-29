from django.contrib.auth.decorators import login_required
from django.shortcuts import render


MARKET_DATA = {

    "rice": [
        {
            "market": "Lucknow Mandi",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "price": 2350,
            "unit": "Quintal",
            "change": "+2.4%",
        },
        {
            "market": "Hardoi Mandi",
            "district": "Hardoi",
            "state": "Uttar Pradesh",
            "price": 2280,
            "unit": "Quintal",
            "change": "+1.8%",
        },
        {
            "market": "Sitapur Mandi",
            "district": "Sitapur",
            "state": "Uttar Pradesh",
            "price": 2310,
            "unit": "Quintal",
            "change": "-0.6%",
        },
    ],

    "wheat": [
        {
            "market": "Lucknow Mandi",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "price": 2420,
            "unit": "Quintal",
            "change": "+1.2%",
        },
        {
            "market": "Hardoi Mandi",
            "district": "Hardoi",
            "state": "Uttar Pradesh",
            "price": 2380,
            "unit": "Quintal",
            "change": "+0.8%",
        },
    ],

    "tomato": [
        {
            "market": "Lucknow Mandi",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "price": 1850,
            "unit": "Quintal",
            "change": "+5.2%",
        },
        {
            "market": "Sitapur Mandi",
            "district": "Sitapur",
            "state": "Uttar Pradesh",
            "price": 1720,
            "unit": "Quintal",
            "change": "-1.4%",
        },
    ],

    "potato": [
        {
            "market": "Lucknow Mandi",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "price": 1450,
            "unit": "Quintal",
            "change": "+2.1%",
        },
        {
            "market": "Agra Mandi",
            "district": "Agra",
            "state": "Uttar Pradesh",
            "price": 1510,
            "unit": "Quintal",
            "change": "+3.5%",
        },
    ],

    "maize": [
        {
            "market": "Lucknow Mandi",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "price": 2180,
            "unit": "Quintal",
            "change": "+1.7%",
        },
    ],
}


@login_required(login_url="accounts:login")
def mandi_home(request):

    crop = request.GET.get("crop", "rice")

    markets = MARKET_DATA.get(
        crop,
        []
    )

    crop_names = {
        "rice": "Rice",
        "wheat": "Wheat",
        "tomato": "Tomato",
        "potato": "Potato",
        "maize": "Maize",
    }

    return render(
        request,
        "mandi/mandi.html",
        {
            "markets": markets,
            "selected_crop": crop,
            "crop_name": crop_names.get(
                crop,
                crop.title()
            ),
        }
    )