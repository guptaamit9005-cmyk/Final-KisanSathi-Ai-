
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET


# Sample government schemes data
SCHEMES = [
    {
        "id": 1,
        "name": "PM-KISAN",
        "description": "Income support scheme for eligible farmer families.",
        "category": "Financial Assistance",
        "benefits": "Financial assistance subject to eligibility.",
        "official_url": "https://pmkisan.gov.in/",
    },
    {
        "id": 2,
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "description": "Crop insurance scheme for eligible farmers.",
        "category": "Crop Insurance",
        "benefits": "Insurance protection against specified crop losses.",
        "official_url": "https://pmfby.gov.in/",
    },
    {
        "id": 3,
        "name": "Kisan Credit Card",
        "description": "Credit facility for eligible farmers.",
        "category": "Agricultural Credit",
        "benefits": "Agricultural credit subject to eligibility.",
        "official_url": "https://www.myscheme.gov.in/",
    },
]


# Government schemes webpage
def scheme_list(request):
    return render(
        request,
        "government_schemes/scheme_list.html",
        {"schemes": SCHEMES}
    )


# Government schemes JSON API
@require_GET
def scheme_api(request):
    return JsonResponse({
        "success": True,
        "count": len(SCHEMES),
        "schemes": SCHEMES,
    })