from django.contrib.auth.decorators import login_required
from django.shortcuts import render


LEARNING_ROADMAPS = [
    {
        "id": "rice",
        "crop": "Rice",
        "title": "Rice Farming Roadmap",
        "icon": "🌾",
        "level": "Beginner",
        "duration": "12 Weeks",
        "description": "Learn modern rice cultivation from seed selection to harvesting.",
        "steps": [
            {
                "title": "Choose the Right Variety",
                "icon": "🌱",
                "description": "Select a rice variety according to your region, season, water availability and market demand.",
                "modern": [
                    "Use certified quality seeds.",
                    "Prefer varieties recommended for your local agro-climatic conditions.",
                    "Check seed quality before sowing."
                ]
            },
            {
                "title": "Prepare the Field",
                "icon": "🚜",
                "description": "Prepare the field properly before planting.",
                "modern": [
                    "Use laser land levelling where available.",
                    "Maintain proper field drainage.",
                    "Use soil-test information for nutrient planning."
                ]
            },
            {
                "title": "Modern Sowing",
                "icon": "🌾",
                "description": "Choose an appropriate establishment method for your crop and conditions.",
                "modern": [
                    "Consider mechanical transplanting where suitable.",
                    "Use recommended plant spacing.",
                    "Avoid unnecessary dense planting."
                ]
            },
            {
                "title": "Smart Irrigation",
                "icon": "💧",
                "description": "Manage water according to crop stage and field condition.",
                "modern": [
                    "Monitor field moisture.",
                    "Avoid unnecessary standing water where not required.",
                    "Use efficient irrigation methods where practical."
                ]
            },
            {
                "title": "Nutrient Management",
                "icon": "🧪",
                "description": "Provide nutrients according to crop requirement and soil condition.",
                "modern": [
                    "Use soil-test based fertilizer planning.",
                    "Apply nutrients at appropriate crop stages.",
                    "Avoid excessive fertilizer application."
                ]
            },
            {
                "title": "Disease & Pest Management",
                "icon": "🔍",
                "description": "Regularly monitor the crop for disease and pest symptoms.",
                "modern": [
                    "Inspect leaves regularly.",
                    "Use crop-image analysis for early warning.",
                    "Follow integrated pest management practices."
                ]
            },
            {
                "title": "Harvest & Storage",
                "icon": "🌾",
                "description": "Harvest at the appropriate maturity stage and store safely.",
                "modern": [
                    "Monitor crop maturity.",
                    "Reduce harvesting losses.",
                    "Use clean and dry storage conditions."
                ]
            }
        ]
    },

    {
        "id": "tomato",
        "crop": "Tomato",
        "title": "Tomato Farming Roadmap",
        "icon": "🍅",
        "level": "Beginner",
        "duration": "10 Weeks",
        "description": "Learn tomato cultivation, disease prevention and modern farm management.",
        "steps": [
            {
                "title": "Select Quality Seeds",
                "icon": "🌱",
                "description": "Choose suitable varieties based on season, region and market requirement.",
                "modern": [
                    "Use certified seeds.",
                    "Select varieties suited to your local conditions.",
                    "Check disease resistance traits where relevant."
                ]
            },
            {
                "title": "Nursery Preparation",
                "icon": "🌿",
                "description": "Raise healthy seedlings before transplanting.",
                "modern": [
                    "Use clean nursery media.",
                    "Maintain suitable moisture.",
                    "Protect seedlings from pests and diseases."
                ]
            },
            {
                "title": "Transplanting",
                "icon": "🌱",
                "description": "Transplant healthy seedlings with appropriate spacing.",
                "modern": [
                    "Use recommended spacing.",
                    "Avoid damaged seedlings.",
                    "Transplant during suitable weather conditions."
                ]
            },
            {
                "title": "Drip Irrigation",
                "icon": "💧",
                "description": "Manage irrigation efficiently according to crop needs.",
                "modern": [
                    "Consider drip irrigation.",
                    "Monitor soil moisture.",
                    "Avoid over-irrigation."
                ]
            },
            {
                "title": "Mulching",
                "icon": "🍃",
                "description": "Use suitable mulch to help manage soil moisture and weeds.",
                "modern": [
                    "Consider organic or suitable plastic mulch.",
                    "Monitor soil moisture.",
                    "Manage weeds early."
                ]
            },
            {
                "title": "Disease Monitoring",
                "icon": "🔬",
                "description": "Regularly inspect leaves, stems and fruits.",
                "modern": [
                    "Use KisanSathi crop-image analysis.",
                    "Record disease symptoms.",
                    "Take action after identifying the likely problem."
                ]
            },
            {
                "title": "Harvest & Market",
                "icon": "🧺",
                "description": "Harvest carefully and monitor market conditions.",
                "modern": [
                    "Harvest according to market requirements.",
                    "Reduce physical damage during handling.",
                    "Check mandi prices before selling."
                ]
            }
        ]
    },

    {
        "id": "wheat",
        "crop": "Wheat",
        "title": "Wheat Farming Roadmap",
        "icon": "🌾",
        "level": "Beginner",
        "duration": "14 Weeks",
        "description": "A step-by-step guide to modern wheat cultivation.",
        "steps": [
            {
                "title": "Seed Selection",
                "icon": "🌱",
                "description": "Select suitable quality seed for your region and season.",
                "modern": [
                    "Use certified seed.",
                    "Choose suitable varieties.",
                    "Maintain proper seed quality."
                ]
            },
            {
                "title": "Field Preparation",
                "icon": "🚜",
                "description": "Prepare the field with suitable soil and moisture conditions.",
                "modern": [
                    "Use conservation agriculture practices where suitable.",
                    "Avoid unnecessary tillage.",
                    "Maintain proper field condition."
                ]
            },
            {
                "title": "Precision Sowing",
                "icon": "🌾",
                "description": "Maintain suitable seed rate, depth and spacing.",
                "modern": [
                    "Consider seed drills.",
                    "Maintain uniform sowing depth.",
                    "Avoid excessive seed rate."
                ]
            },
            {
                "title": "Smart Irrigation",
                "icon": "💧",
                "description": "Irrigate according to important crop growth stages.",
                "modern": [
                    "Monitor soil moisture.",
                    "Prioritize critical crop stages.",
                    "Avoid unnecessary irrigation."
                ]
            },
            {
                "title": "Nutrient Management",
                "icon": "🧪",
                "description": "Manage nutrients according to soil and crop requirements.",
                "modern": [
                    "Use soil-test based planning.",
                    "Split nutrient application where appropriate.",
                    "Monitor crop growth."
                ]
            },
            {
                "title": "Disease Monitoring",
                "icon": "🔍",
                "description": "Monitor the crop for disease and pest symptoms.",
                "modern": [
                    "Regularly inspect leaves.",
                    "Use crop-image analysis.",
                    "Maintain field records."
                ]
            },
            {
                "title": "Harvest",
                "icon": "🚜",
                "description": "Harvest when the crop reaches appropriate maturity.",
                "modern": [
                    "Monitor grain maturity.",
                    "Reduce harvesting losses.",
                    "Store grain in dry conditions."
                ]
            }
        ]
    },

    {
        "id": "potato",
        "crop": "Potato",
        "title": "Potato Farming Roadmap",
        "icon": "🥔",
        "level": "Intermediate",
        "duration": "12 Weeks",
        "description": "Learn potato production with modern crop monitoring.",
        "steps": [
            {
                "title": "Quality Seed Tubers",
                "icon": "🥔",
                "description": "Start with healthy and suitable planting material.",
                "modern": [
                    "Use quality seed tubers.",
                    "Avoid diseased planting material.",
                    "Select suitable varieties."
                ]
            },
            {
                "title": "Soil & Field Preparation",
                "icon": "🚜",
                "description": "Prepare suitable soil conditions before planting.",
                "modern": [
                    "Maintain proper drainage.",
                    "Use soil-test information.",
                    "Prepare suitable planting beds."
                ]
            },
            {
                "title": "Planting",
                "icon": "🌱",
                "description": "Maintain appropriate spacing and planting depth.",
                "modern": [
                    "Use suitable mechanized planting where available.",
                    "Maintain uniform spacing.",
                    "Avoid waterlogging."
                ]
            },
            {
                "title": "Irrigation Management",
                "icon": "💧",
                "description": "Maintain appropriate soil moisture.",
                "modern": [
                    "Monitor soil moisture.",
                    "Avoid excessive irrigation.",
                    "Use efficient irrigation systems where practical."
                ]
            },
            {
                "title": "Disease Monitoring",
                "icon": "🔬",
                "description": "Monitor foliage for early signs of disease.",
                "modern": [
                    "Use KisanSathi image analysis.",
                    "Inspect fields regularly.",
                    "Remove or manage affected plants according to expert guidance."
                ]
            },
            {
                "title": "Harvest & Storage",
                "icon": "🧺",
                "description": "Harvest carefully and store under suitable conditions.",
                "modern": [
                    "Reduce mechanical damage.",
                    "Grade harvested potatoes.",
                    "Maintain suitable storage conditions."
                ]
            }
        ]
    },

    {
        "id": "maize",
        "crop": "Maize",
        "title": "Maize Farming Roadmap",
        "icon": "🌽",
        "level": "Beginner",
        "duration": "12 Weeks",
        "description": "Learn modern maize cultivation and crop monitoring.",
        "steps": [
            {
                "title": "Choose Suitable Seed",
                "icon": "🌱",
                "description": "Select suitable quality seed according to your farming conditions.",
                "modern": [
                    "Use certified seed.",
                    "Select suitable variety.",
                    "Check seed quality."
                ]
            },
            {
                "title": "Precision Sowing",
                "icon": "🌽",
                "description": "Maintain suitable plant population and spacing.",
                "modern": [
                    "Consider precision planters.",
                    "Maintain uniform spacing.",
                    "Avoid excessive plant population."
                ]
            },
            {
                "title": "Smart Irrigation",
                "icon": "💧",
                "description": "Manage water according to crop requirement.",
                "modern": [
                    "Monitor soil moisture.",
                    "Avoid water stress during critical stages.",
                    "Use efficient irrigation where possible."
                ]
            },
            {
                "title": "Nutrient Management",
                "icon": "🧪",
                "description": "Plan nutrients according to soil and crop needs.",
                "modern": [
                    "Use soil-test based recommendations.",
                    "Apply nutrients at suitable stages.",
                    "Avoid excessive fertilizer."
                ]
            },
            {
                "title": "Pest & Disease Monitoring",
                "icon": "🔍",
                "description": "Regularly inspect plants for pest and disease symptoms.",
                "modern": [
                    "Use crop-image analysis.",
                    "Maintain regular field scouting.",
                    "Use integrated pest management."
                ]
            },
            {
                "title": "Harvest",
                "icon": "🚜",
                "description": "Harvest at suitable maturity.",
                "modern": [
                    "Monitor crop maturity.",
                    "Reduce harvest losses.",
                    "Store grain under suitable dry conditions."
                ]
            }
        ]
    }
]


@login_required(login_url="accounts:login")
def learning_home(request):

    selected_crop = request.GET.get("crop", "").strip().lower()

    roadmaps = LEARNING_ROADMAPS

    if selected_crop:
        roadmaps = [
            roadmap
            for roadmap in roadmaps
            if roadmap["id"] == selected_crop
        ]

    context = {
        "roadmaps": roadmaps,
        "selected_crop": selected_crop,
        "all_roadmaps": LEARNING_ROADMAPS,
    }

    return render(
        request,
        "encyclopedia/learning.html",
        context
    )