from decimal import Decimal
import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import MandiPrice


# Comprehensive, Realistic Crop Market Dataset (All major categories in Indian Mandis)
ALL_CROPS_DATA = [
    # Cereals & Grains
    {
        "id": "wheat",
        "name": "Wheat (गेहूं)",
        "category": "Cereals & Grains",
        "icon": "🌾",
        "season": "Rabi",
        "msp": 2275,
        "avg_price": 2420,
        "unit": "Quintal",
        "trend": "+1.8%",
        "trend_direction": "up",
        "top_market": "Khanna Mandi (Punjab)",
        "markets": [
            {"market": "Khanna Mandi", "district": "Ludhiana", "state": "Punjab", "variety": "Sharbati / PBW-343", "price": 2550, "min_price": 2350, "max_price": 2600, "arrival": "1,200 Qtl", "change": "+2.1%"},
            {"market": "Lucknow Mandi", "district": "Lucknow", "state": "Uttar Pradesh", "variety": "Lokwan", "price": 2420, "min_price": 2320, "max_price": 2480, "arrival": "850 Qtl", "change": "+1.2%"},
            {"market": "Hardoi Mandi", "district": "Hardoi", "state": "Uttar Pradesh", "variety": "Dara", "price": 2380, "min_price": 2280, "max_price": 2420, "arrival": "620 Qtl", "change": "+0.8%"},
            {"market": "Karnal Mandi", "district": "Karnal", "state": "Haryana", "variety": "HD-2967", "price": 2470, "min_price": 2350, "max_price": 2520, "arrival": "950 Qtl", "change": "+1.5%"},
            {"market": "Sehore Mandi", "district": "Sehore", "state": "Madhya Pradesh", "variety": "Sharbati Premium", "price": 2890, "min_price": 2650, "max_price": 3100, "arrival": "420 Qtl", "change": "+3.2%"},
        ]
    },
    {
        "id": "rice",
        "name": "Paddy / Rice (धान / चावल)",
        "category": "Cereals & Grains",
        "icon": "🍚",
        "season": "Kharif",
        "msp": 2300,
        "avg_price": 2520,
        "unit": "Quintal",
        "trend": "+2.4%",
        "trend_direction": "up",
        "top_market": "Karnal Mandi (Haryana)",
        "markets": [
            {"market": "Karnal Mandi", "district": "Karnal", "state": "Haryana", "variety": "Basmati 1121", "price": 3650, "min_price": 3400, "max_price": 3800, "arrival": "1,850 Qtl", "change": "+4.1%"},
            {"market": "Lucknow Mandi", "district": "Lucknow", "state": "Uttar Pradesh", "variety": "Common (Mansoori)", "price": 2350, "min_price": 2200, "max_price": 2450, "arrival": "1,100 Qtl", "change": "+2.4%"},
            {"market": "Sitapur Mandi", "district": "Sitapur", "state": "Uttar Pradesh", "variety": "Sarju 52", "price": 2310, "min_price": 2180, "max_price": 2390, "arrival": "900 Qtl", "change": "-0.6%"},
            {"market": "Burdwan Mandi", "district": "Purba Bardhaman", "state": "West Bengal", "variety": "Miniket", "price": 2680, "min_price": 2500, "max_price": 2800, "arrival": "1,400 Qtl", "change": "+1.9%"},
            {"market": "Raipur Mandi", "district": "Raipur", "state": "Chhattisgarh", "variety": "Swarna", "price": 2380, "min_price": 2250, "max_price": 2460, "arrival": "1,250 Qtl", "change": "+1.1%"},
        ]
    },
    {
        "id": "maize",
        "name": "Maize / Corn (मक्का)",
        "category": "Cereals & Grains",
        "icon": "🌽",
        "season": "Kharif",
        "msp": 2090,
        "avg_price": 2210,
        "unit": "Quintal",
        "trend": "+1.7%",
        "trend_direction": "up",
        "top_market": "Gulabbagh (Bihar)",
        "markets": [
            {"market": "Gulabbagh Mandi", "district": "Purnea", "state": "Bihar", "variety": "Yellow Hybrid", "price": 2240, "min_price": 2120, "max_price": 2320, "arrival": "2,100 Qtl", "change": "+2.3%"},
            {"market": "Davangere Mandi", "district": "Davangere", "state": "Karnataka", "variety": "Hybrid White", "price": 2190, "min_price": 2080, "max_price": 2270, "arrival": "1,300 Qtl", "change": "+1.4%"},
            {"market": "Lucknow Mandi", "district": "Lucknow", "state": "Uttar Pradesh", "variety": "Yellow Local", "price": 2180, "min_price": 2050, "max_price": 2260, "arrival": "450 Qtl", "change": "+1.7%"},
            {"market": "Chhindwara Mandi", "district": "Chhindwara", "state": "Madhya Pradesh", "variety": "Sweet Corn / Feed", "price": 2230, "min_price": 2100, "max_price": 2340, "arrival": "820 Qtl", "change": "+0.9%"},
        ]
    },
    {
        "id": "barley",
        "name": "Barley / Jau (जौ)",
        "category": "Cereals & Grains",
        "icon": "🌾",
        "season": "Rabi",
        "msp": 1850,
        "avg_price": 1980,
        "unit": "Quintal",
        "trend": "+0.5%",
        "trend_direction": "up",
        "top_market": "Jaipur Mandi (Rajasthan)",
        "markets": [
            {"market": "Jaipur Mandi", "district": "Jaipur", "state": "Rajasthan", "variety": "Malt Grade", "price": 2080, "min_price": 1950, "max_price": 2190, "arrival": "400 Qtl", "change": "+1.0%"},
            {"market": "Alwar Mandi", "district": "Alwar", "state": "Rajasthan", "variety": "Feed Grade", "price": 1940, "min_price": 1850, "max_price": 2010, "arrival": "310 Qtl", "change": "-0.4%"},
            {"market": "Sirsa Mandi", "district": "Sirsa", "state": "Haryana", "variety": "Ordinary", "price": 1920, "min_price": 1820, "max_price": 1990, "arrival": "280 Qtl", "change": "+0.7%"},
        ]
    },
    {
        "id": "bajra",
        "name": "Pearl Millet / Bajra (बाजरा)",
        "category": "Cereals & Grains",
        "icon": "🌾",
        "season": "Kharif",
        "msp": 2500,
        "avg_price": 2440,
        "unit": "Quintal",
        "trend": "+1.3%",
        "trend_direction": "up",
        "top_market": "Agra Mandi (Uttar Pradesh)",
        "markets": [
            {"market": "Agra Mandi", "district": "Agra", "state": "Uttar Pradesh", "variety": "Desi Bold", "price": 2480, "min_price": 2360, "max_price": 2560, "arrival": "650 Qtl", "change": "+1.6%"},
            {"market": "Jodhpur Mandi", "district": "Jodhpur", "state": "Rajasthan", "variety": "Hybrid Green", "price": 2420, "min_price": 2300, "max_price": 2510, "arrival": "800 Qtl", "change": "+0.9%"},
            {"market": "Bhiwani Mandi", "district": "Bhiwani", "state": "Haryana", "variety": "Common", "price": 2410, "min_price": 2290, "max_price": 2490, "arrival": "490 Qtl", "change": "+1.2%"},
        ]
    },

    # Pulses & Legumes
    {
        "id": "chana",
        "name": "Chickpea / Gram / Chana (चना)",
        "category": "Pulses & Legumes",
        "icon": "🧆",
        "season": "Rabi",
        "msp": 5440,
        "avg_price": 6150,
        "unit": "Quintal",
        "trend": "+3.1%",
        "trend_direction": "up",
        "top_market": "Indore Mandi (Madhya Pradesh)",
        "markets": [
            {"market": "Indore Mandi", "district": "Indore", "state": "Madhya Pradesh", "variety": "Desi Kantewala", "price": 6280, "min_price": 5950, "max_price": 6450, "arrival": "1,100 Qtl", "change": "+3.5%"},
            {"market": "Bikaner Mandi", "district": "Bikaner", "state": "Rajasthan", "variety": "Kabuli Dollar", "price": 8450, "min_price": 7900, "max_price": 9100, "arrival": "650 Qtl", "change": "+4.2%"},
            {"market": "Akola Mandi", "district": "Akola", "state": "Maharashtra", "variety": "Annagiri / Chana", "price": 6050, "min_price": 5800, "max_price": 6200, "arrival": "780 Qtl", "change": "+2.0%"},
            {"market": "Kanpur Mandi", "district": "Kanpur", "state": "Uttar Pradesh", "variety": "Desi Yellow", "price": 6120, "min_price": 5880, "max_price": 6300, "arrival": "540 Qtl", "change": "+1.8%"},
        ]
    },
    {
        "id": "tur",
        "name": "Pigeon Pea / Arhar / Tur (अरहर / तुअर)",
        "category": "Pulses & Legumes",
        "icon": "🍲",
        "season": "Kharif",
        "msp": 7550,
        "avg_price": 9850,
        "unit": "Quintal",
        "trend": "+4.6%",
        "trend_direction": "up",
        "top_market": "Kalaburagi / Gulbarga (Karnataka)",
        "markets": [
            {"market": "Kalaburagi Mandi", "district": "Kalaburagi", "state": "Karnataka", "variety": "Gulyal / Red Tur", "price": 10250, "min_price": 9600, "max_price": 10700, "arrival": "1,450 Qtl", "change": "+5.2%"},
            {"market": "Latur Mandi", "district": "Latur", "state": "Maharashtra", "variety": "Pink / White Marathwada", "price": 9950, "min_price": 9300, "max_price": 10400, "arrival": "1,200 Qtl", "change": "+4.8%"},
            {"market": "Katni Mandi", "district": "Katni", "state": "Madhya Pradesh", "variety": "Desi Arhar", "price": 9600, "min_price": 9100, "max_price": 10050, "arrival": "480 Qtl", "change": "+3.9%"},
            {"market": "Varanasi Mandi", "district": "Varanasi", "state": "Uttar Pradesh", "variety": "Local Fat", "price": 9780, "min_price": 9250, "max_price": 10200, "arrival": "390 Qtl", "change": "+4.1%"},
        ]
    },
    {
        "id": "moong",
        "name": "Green Gram / Moong (मूंग)",
        "category": "Pulses & Legumes",
        "icon": "🟢",
        "season": "Kharif / Zaid",
        "msp": 8558,
        "avg_price": 8420,
        "unit": "Quintal",
        "trend": "-1.1%",
        "trend_direction": "down",
        "top_market": "Merta City (Rajasthan)",
        "markets": [
            {"market": "Merta City Mandi", "district": "Nagaur", "state": "Rajasthan", "variety": "Shiny Green Bold", "price": 8650, "min_price": 8100, "max_price": 9100, "arrival": "920 Qtl", "change": "+0.5%"},
            {"market": "Hardoi Mandi", "district": "Hardoi", "state": "Uttar Pradesh", "variety": "Local Medium", "price": 8280, "min_price": 7800, "max_price": 8600, "arrival": "320 Qtl", "change": "-1.8%"},
            {"market": "Jalna Mandi", "district": "Jalna", "state": "Maharashtra", "variety": "Hybrid Green", "price": 8390, "min_price": 7950, "max_price": 8700, "arrival": "540 Qtl", "change": "-0.9%"},
        ]
    },
    {
        "id": "urad",
        "name": "Black Gram / Urad (उड़द)",
        "category": "Pulses & Legumes",
        "icon": "⚫",
        "season": "Kharif",
        "msp": 7400,
        "avg_price": 7850,
        "unit": "Quintal",
        "trend": "+2.0%",
        "trend_direction": "up",
        "top_market": "Latur Mandi (Maharashtra)",
        "markets": [
            {"market": "Latur Mandi", "district": "Latur", "state": "Maharashtra", "variety": "Black Bold", "price": 8120, "min_price": 7600, "max_price": 8450, "arrival": "680 Qtl", "change": "+2.4%"},
            {"market": "Jabalpur Mandi", "district": "Jabalpur", "state": "Madhya Pradesh", "variety": "Desi", "price": 7760, "min_price": 7300, "max_price": 8100, "arrival": "410 Qtl", "change": "+1.7%"},
            {"market": "Banda Mandi", "district": "Banda", "state": "Uttar Pradesh", "variety": "Bundelkhand Black", "price": 7680, "min_price": 7250, "max_price": 8000, "arrival": "350 Qtl", "change": "+1.8%"},
        ]
    },

    # Oilseeds
    {
        "id": "mustard",
        "name": "Mustard / Sarson (सरसों / राई)",
        "category": "Oilseeds",
        "icon": "🌼",
        "season": "Rabi",
        "msp": 5650,
        "avg_price": 5780,
        "unit": "Quintal",
        "trend": "+1.6%",
        "trend_direction": "up",
        "top_market": "Bharatpur Mandi (Rajasthan)",
        "markets": [
            {"market": "Bharatpur Mandi", "district": "Bharatpur", "state": "Rajasthan", "variety": "42% Oil Condition", "price": 5940, "min_price": 5680, "max_price": 6120, "arrival": "2,400 Qtl", "change": "+2.0%"},
            {"market": "Jaipur Mandi", "district": "Jaipur", "state": "Rajasthan", "variety": "Yellow / Black Sarson", "price": 5860, "min_price": 5620, "max_price": 6050, "arrival": "1,800 Qtl", "change": "+1.5%"},
            {"market": "Agra Mandi", "district": "Agra", "state": "Uttar Pradesh", "variety": "Desi Mustard", "price": 5720, "min_price": 5500, "max_price": 5900, "arrival": "1,100 Qtl", "change": "+1.4%"},
            {"market": "Hisar Mandi", "district": "Hisar", "state": "Haryana", "variety": "Raya / Sarson", "price": 5790, "min_price": 5550, "max_price": 5950, "arrival": "850 Qtl", "change": "+1.2%"},
        ]
    },
    {
        "id": "soybean",
        "name": "Soybean (सोयाबीन)",
        "category": "Oilseeds",
        "icon": "🌱",
        "season": "Kharif",
        "msp": 4892,
        "avg_price": 4580,
        "unit": "Quintal",
        "trend": "+2.8%",
        "trend_direction": "up",
        "top_market": "Indore Mandi (Madhya Pradesh)",
        "markets": [
            {"market": "Indore Mandi", "district": "Indore", "state": "Madhya Pradesh", "variety": "Yellow Grade A (JS-9560)", "price": 4720, "min_price": 4450, "max_price": 4880, "arrival": "3,200 Qtl", "change": "+3.1%"},
            {"market": "Ujjain Mandi", "district": "Ujjain", "state": "Madhya Pradesh", "variety": "Yellow Commercial", "price": 4640, "min_price": 4380, "max_price": 4790, "arrival": "2,400 Qtl", "change": "+2.6%"},
            {"market": "Nagpur Mandi", "district": "Nagpur", "state": "Maharashtra", "variety": "JS-335", "price": 4550, "min_price": 4300, "max_price": 4680, "arrival": "1,600 Qtl", "change": "+2.4%"},
            {"market": "Kota Mandi", "district": "Kota", "state": "Rajasthan", "variety": "Dry Clean", "price": 4590, "min_price": 4350, "max_price": 4720, "arrival": "1,150 Qtl", "change": "+2.2%"},
        ]
    },
    {
        "id": "groundnut",
        "name": "Groundnut / Peanut (मूंगफली)",
        "category": "Oilseeds",
        "icon": "🥜",
        "season": "Kharif",
        "msp": 6783,
        "avg_price": 6950,
        "unit": "Quintal",
        "trend": "+1.9%",
        "trend_direction": "up",
        "top_market": "Rajkot Mandi (Gujarat)",
        "markets": [
            {"market": "Rajkot Mandi", "district": "Rajkot", "state": "Gujarat", "variety": "G-20 / Bold Pods", "price": 7350, "min_price": 6800, "max_price": 7650, "arrival": "2,800 Qtl", "change": "+2.3%"},
            {"market": "Gondal Mandi", "district": "Rajkot", "state": "Gujarat", "variety": "TJ / Java Bold", "price": 7180, "min_price": 6700, "max_price": 7450, "arrival": "2,100 Qtl", "change": "+1.8%"},
            {"market": "Bikaner Mandi", "district": "Bikaner", "state": "Rajasthan", "variety": "Desi Pods", "price": 6750, "min_price": 6300, "max_price": 7050, "arrival": "1,100 Qtl", "change": "+1.4%"},
        ]
    },

    # Commercial & Cash Crops
    {
        "id": "cotton",
        "name": "Cotton / Kapas (कपास)",
        "category": "Commercial Crops",
        "icon": "☁️",
        "season": "Kharif",
        "msp": 7121,
        "avg_price": 7450,
        "unit": "Quintal",
        "trend": "+2.5%",
        "trend_direction": "up",
        "top_market": "Rajkot Mandi (Gujarat)",
        "markets": [
            {"market": "Rajkot Mandi", "district": "Rajkot", "state": "Gujarat", "variety": "Shankar-6 Long Staple", "price": 7680, "min_price": 7200, "max_price": 7950, "arrival": "3,400 Qtl", "change": "+2.9%"},
            {"market": "Warangal Mandi", "district": "Warangal", "state": "Telangana", "variety": "Medium Staple", "price": 7420, "min_price": 7000, "max_price": 7680, "arrival": "1,900 Qtl", "change": "+2.2%"},
            {"market": "Abohar Mandi", "district": "Fazilka", "state": "Punjab", "variety": "Bt Cotton First Picking", "price": 7510, "min_price": 7150, "max_price": 7780, "arrival": "1,100 Qtl", "change": "+2.0%"},
        ]
    },
    {
        "id": "sugarcane",
        "name": "Sugarcane (गन्ना)",
        "category": "Commercial Crops",
        "icon": "🎋",
        "season": "Perennial",
        "msp": 340,
        "avg_price": 385,
        "unit": "Quintal",
        "trend": "0.0%",
        "trend_direction": "neutral",
        "top_market": "Muzaffarnagar (Uttar Pradesh)",
        "markets": [
            {"market": "Muzaffarnagar Mandi", "district": "Muzaffarnagar", "state": "Uttar Pradesh", "variety": "Co-0238 Early Recovery", "price": 395, "min_price": 380, "max_price": 410, "arrival": "8,500 Qtl", "change": "0.0%"},
            {"market": "Kolhapur Mandi", "district": "Kolhapur", "state": "Maharashtra", "variety": "High Recovery Sucrose", "price": 385, "min_price": 370, "max_price": 395, "arrival": "7,200 Qtl", "change": "0.0%"},
            {"market": "Meerut Mandi", "district": "Meerut", "state": "Uttar Pradesh", "variety": "General Cane", "price": 380, "min_price": 365, "max_price": 390, "arrival": "6,100 Qtl", "change": "0.0%"},
        ]
    },

    # Vegetables
    {
        "id": "tomato",
        "name": "Tomato (टमाटर)",
        "category": "Vegetables",
        "icon": "🍅",
        "season": "Year-round",
        "msp": None,
        "avg_price": 1820,
        "unit": "Quintal",
        "trend": "+5.2%",
        "trend_direction": "up",
        "top_market": "Kolar Mandi (Karnataka)",
        "markets": [
            {"market": "Kolar Mandi", "district": "Kolar", "state": "Karnataka", "variety": "Hybrid Red Solid", "price": 2150, "min_price": 1800, "max_price": 2400, "arrival": "3,800 Qtl", "change": "+6.8%"},
            {"market": "Lucknow Mandi", "district": "Lucknow", "state": "Uttar Pradesh", "variety": "Local Hybrid", "price": 1850, "min_price": 1500, "max_price": 2100, "arrival": "1,400 Qtl", "change": "+5.2%"},
            {"market": "Sitapur Mandi", "district": "Sitapur", "state": "Uttar Pradesh", "variety": "Desi", "price": 1720, "min_price": 1400, "max_price": 1950, "arrival": "980 Qtl", "change": "-1.4%"},
            {"market": "Nashik Mandi", "district": "Nashik", "state": "Maharashtra", "variety": "Pusa Ruby / Abhinav", "price": 1920, "min_price": 1600, "max_price": 2200, "arrival": "2,200 Qtl", "change": "+4.3%"},
            {"market": "Azadpur Mandi", "district": "New Delhi", "state": "Delhi", "variety": "Graded Pack", "price": 2280, "min_price": 1900, "max_price": 2550, "arrival": "4,500 Qtl", "change": "+5.9%"},
        ]
    },
    {
        "id": "potato",
        "name": "Potato (आलू)",
        "category": "Vegetables",
        "icon": "🥔",
        "season": "Rabi",
        "msp": None,
        "avg_price": 1490,
        "unit": "Quintal",
        "trend": "+2.1%",
        "trend_direction": "up",
        "top_market": "Agra Mandi (Uttar Pradesh)",
        "markets": [
            {"market": "Agra Mandi", "district": "Agra", "state": "Uttar Pradesh", "variety": "Kufri Bahar / Pukhraj", "price": 1540, "min_price": 1380, "max_price": 1680, "arrival": "5,600 Qtl", "change": "+3.5%"},
            {"market": "Farrukhabad Mandi", "district": "Farrukhabad", "state": "Uttar Pradesh", "variety": "Chipsona / Jyoti", "price": 1510, "min_price": 1350, "max_price": 1640, "arrival": "4,800 Qtl", "change": "+2.8%"},
            {"market": "Lucknow Mandi", "district": "Lucknow", "state": "Uttar Pradesh", "variety": "Desi Red / White", "price": 1450, "min_price": 1300, "max_price": 1580, "arrival": "2,100 Qtl", "change": "+2.1%"},
            {"market": "Jalandhar Mandi", "district": "Jalandhar", "state": "Punjab", "variety": "Table Potato", "price": 1420, "min_price": 1280, "max_price": 1540, "arrival": "3,100 Qtl", "change": "+1.4%"},
            {"market": "Hooghly Mandi", "district": "Hooghly", "state": "West Bengal", "variety": "Jyoti", "price": 1580, "min_price": 1420, "max_price": 1720, "arrival": "3,900 Qtl", "change": "+2.6%"},
        ]
    },
    {
        "id": "onion",
        "name": "Onion (प्याज)",
        "category": "Vegetables",
        "icon": "🧅",
        "season": "Year-round",
        "msp": None,
        "avg_price": 2850,
        "unit": "Quintal",
        "trend": "+4.8%",
        "trend_direction": "up",
        "top_market": "Lasalgaon Mandi (Maharashtra)",
        "markets": [
            {"market": "Lasalgaon Mandi", "district": "Nashik", "state": "Maharashtra", "variety": "Red Garwa / Unhalee", "price": 3150, "min_price": 2600, "max_price": 3450, "arrival": "6,500 Qtl", "change": "+5.4%"},
            {"market": "Pimpalgaon Mandi", "district": "Nashik", "state": "Maharashtra", "variety": "Medium Red", "price": 2980, "min_price": 2500, "max_price": 3280, "arrival": "4,800 Qtl", "change": "+4.9%"},
            {"market": "Indore Mandi", "district": "Indore", "state": "Madhya Pradesh", "variety": "Local Red", "price": 2680, "min_price": 2200, "max_price": 2950, "arrival": "2,300 Qtl", "change": "+3.8%"},
            {"market": "Lucknow Mandi", "district": "Lucknow", "state": "Uttar Pradesh", "variety": "Nashik Onion", "price": 3200, "min_price": 2800, "max_price": 3500, "arrival": "1,500 Qtl", "change": "+4.2%"},
        ]
    },
    {
        "id": "garlic",
        "name": "Garlic / Lehsun (लहसुन)",
        "category": "Vegetables",
        "icon": "🧄",
        "season": "Rabi",
        "msp": None,
        "avg_price": 13500,
        "unit": "Quintal",
        "trend": "+6.4%",
        "trend_direction": "up",
        "top_market": "Mandsaur Mandi (Madhya Pradesh)",
        "markets": [
            {"market": "Mandsaur Mandi", "district": "Mandsaur", "state": "Madhya Pradesh", "variety": "Ooty / Amleta Super Bold", "price": 15800, "min_price": 13000, "max_price": 18500, "arrival": "1,800 Qtl", "change": "+7.2%"},
            {"market": "Neemuch Mandi", "district": "Neemuch", "state": "Madhya Pradesh", "variety": "G-2 / Medium", "price": 14200, "min_price": 11500, "max_price": 16000, "arrival": "1,450 Qtl", "change": "+6.1%"},
            {"market": "Kota Mandi", "district": "Kota", "state": "Rajasthan", "variety": "Desi White", "price": 12800, "min_price": 10500, "max_price": 14500, "arrival": "920 Qtl", "change": "+5.3%"},
        ]
    },
    {
        "id": "chilli",
        "name": "Green / Dry Chilli (हरी मिर्च / सूखी मिर्च)",
        "category": "Vegetables",
        "icon": "🌶️",
        "season": "Year-round",
        "msp": None,
        "avg_price": 18200,
        "unit": "Quintal",
        "trend": "+3.4%",
        "trend_direction": "up",
        "top_market": "Guntur Mandi (Andhra Pradesh)",
        "markets": [
            {"market": "Guntur Mandi", "district": "Guntur", "state": "Andhra Pradesh", "variety": "Teja / Sannam Dry", "price": 21500, "min_price": 18500, "max_price": 24000, "arrival": "3,200 Qtl", "change": "+4.2%"},
            {"market": "Byadgi Mandi", "district": "Haveri", "state": "Karnataka", "variety": "Byadgi Kaddi", "price": 28500, "min_price": 24000, "max_price": 33000, "arrival": "1,400 Qtl", "change": "+5.1%"},
            {"market": "Varanasi Mandi", "district": "Varanasi", "state": "Uttar Pradesh", "variety": "Green Hot Local", "price": 3800, "min_price": 3200, "max_price": 4400, "arrival": "650 Qtl", "change": "+2.8%"},
        ]
    },
]


@login_required(login_url="accounts:login")
def mandi_home(request):
    """
    Renders comprehensive mandi market prices across all crop categories,
    with live search, category filtering, MSP comparison, and interactive calculator.
    """
    selected_crop_id = request.GET.get("crop", "all").strip().lower()
    selected_category = request.GET.get("category", "all").strip()
    search_query = request.GET.get("q", "").strip().lower()

    # Filter crops list
    filtered_crops = []
    all_categories = sorted(list(set(c["category"] for c in ALL_CROPS_DATA)))

    for crop in ALL_CROPS_DATA:
        # Category check
        if selected_category != "all" and crop["category"] != selected_category:
            continue
        
        # Specific crop ID check
        if selected_crop_id != "all" and crop["id"] != selected_crop_id:
            continue

        # Search query check (crop name, market, state, district)
        if search_query:
            query_match = (
                search_query in crop["name"].lower()
                or search_query in crop["category"].lower()
                or any(
                    search_query in m["market"].lower()
                    or search_query in m["district"].lower()
                    or search_query in m["state"].lower()
                    for m in crop["markets"]
                )
            )
            if not query_match:
                continue

        filtered_crops.append(crop)

    # Calculate overall market metrics
    total_markets_tracked = sum(len(c["markets"]) for c in ALL_CROPS_DATA)
    total_crops_count = len(ALL_CROPS_DATA)

    # Current single crop if selected
    active_crop = None
    if selected_crop_id != "all":
        active_crop = next((c for c in ALL_CROPS_DATA if c["id"] == selected_crop_id), None)

    context = {
        "crops": filtered_crops,
        "all_crops": ALL_CROPS_DATA,
        "categories": all_categories,
        "selected_crop_id": selected_crop_id,
        "selected_category": selected_category,
        "search_query": search_query,
        "active_crop": active_crop,
        "total_crops_count": total_crops_count,
        "total_markets_tracked": total_markets_tracked,
        "last_updated": datetime.date.today().strftime("%B %d, %Y"),
    }

    return render(request, "mandi/mandi.html", context)


@login_required(login_url="accounts:login")
def mandi_crop_api(request, crop_id):
    """
    JSON API for interactive calculators & AJAX lookups
    """
    crop = next((c for c in ALL_CROPS_DATA if c["id"] == crop_id.lower()), None)
    if not crop:
        return JsonResponse({"success": False, "error": "Crop not found"}, status=404)

    return JsonResponse({
        "success": True,
        "crop": crop,
    })