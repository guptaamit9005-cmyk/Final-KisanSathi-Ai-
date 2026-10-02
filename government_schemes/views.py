import json
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods
from .models import GovernmentScheme
from .services import check_scheme_eligibility


def scheme_list(request):
    """
    Advanced Government Schemes Directory with search, filters,
    category navigation, quick eligibility finder, and instant links.
    """
    search_query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip().lower()
    state = request.GET.get("state", "").strip()
    farmer_type = request.GET.get("farmer_type", "").strip().lower()

    queryset = GovernmentScheme.objects.filter(is_active=True)

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(benefits__icontains=search_query)
        )

    if category and category != "all":
        queryset = queryset.filter(category=category)

    if state and state != "All India" and state != "all":
        queryset = queryset.filter(
            Q(state="All India") | Q(state__icontains=state)
        )

    if farmer_type and farmer_type != "all" and farmer_type != "any":
        queryset = queryset.filter(
            Q(farmer_type="all") | Q(farmer_type="any") | Q(farmer_type=farmer_type)
        )

    schemes = list(queryset.order_by("title"))

    # Summary statistics across all active schemes
    all_active = GovernmentScheme.objects.filter(is_active=True)
    total_count = all_active.count()
    income_count = all_active.filter(category="income").count()
    insurance_count = all_active.filter(category="insurance").count()
    credit_count = all_active.filter(category="credit").count()
    subsidy_count = all_active.filter(
        category__in=["subsidy", "equipment", "irrigation"]
    ).count()

    categories_list = [
        {"key": "all", "label": "All Schemes", "icon": "🌾", "count": total_count},
        {"key": "income", "label": "Income Support", "icon": "💰", "count": income_count},
        {"key": "insurance", "label": "Crop Insurance", "icon": "🛡️", "count": insurance_count},
        {"key": "credit", "label": "Low-Interest Credit", "icon": "💳", "count": credit_count},
        {"key": "subsidy", "label": "Subsidies & Solar", "icon": "🎁", "count": subsidy_count},
        {"key": "equipment", "label": "Farm Machinery", "icon": "🚜", "count": all_active.filter(category="equipment").count()},
        {"key": "irrigation", "label": "Micro Irrigation", "icon": "💧", "count": all_active.filter(category="irrigation").count()},
    ]

    # JSON representation for client-side search, filter and interactive preview
    schemes_data = []
    for s in all_active.order_by("title"):
        schemes_data.append({
            "id": s.id,
            "title": s.title,
            "slug": s.slug,
            "category": s.category,
            "category_display": s.get_category_display(),
            "category_icon": s.category_icon,
            "state": s.state,
            "farmer_type": s.farmer_type,
            "short_description": s.short_description,
            "benefits": s.benefits,
            "benefits_list": s.benefits_list,
            "eligibility_list": s.eligibility_list,
            "documents_list": s.documents_list,
            "steps_list": s.steps_list,
            "official_url": s.official_url,
            "helpline": s.helpline,
            "detail_url": s.get_absolute_url(),
        })

    context = {
        "schemes": schemes,
        "schemes_json": json.dumps(schemes_data),
        "total_count": total_count,
        "income_count": income_count,
        "insurance_count": insurance_count,
        "credit_count": credit_count,
        "subsidy_count": subsidy_count,
        "categories_list": categories_list,
        "search_query": search_query,
        "selected_category": category,
        "selected_state": state,
        "selected_farmer_type": farmer_type,
    }

    return render(request, "government_schemes/government_schemes.html", context)


def scheme_detail(request, slug):
    """
    Dedicated scheme detail page with comprehensive overview,
    benefits breakdown, eligibility criteria, document checklist,
    step-by-step application instructions, and official links.
    """
    scheme = get_object_or_404(GovernmentScheme, slug=slug, is_active=True)

    # Related schemes in the same category or overall
    related = list(
        GovernmentScheme.objects.filter(is_active=True, category=scheme.category)
        .exclude(id=scheme.id)[:3]
    )
    if len(related) < 3:
        exclude_ids = [scheme.id] + [r.id for r in related]
        filler = list(
            GovernmentScheme.objects.filter(is_active=True)
            .exclude(id__in=exclude_ids)[: 3 - len(related)]
        )
        related.extend(filler)

    context = {
        "scheme": scheme,
        "related_schemes": related,
    }
    return render(request, "government_schemes/detail.html", context)


@require_GET
def scheme_api(request):
    """
    JSON API for fetching schemes list with full attributes.
    """
    schemes = GovernmentScheme.objects.filter(is_active=True).order_by("title")
    data = []
    for s in schemes:
        data.append({
            "id": s.id,
            "title": s.title,
            "slug": s.slug,
            "category": s.category,
            "category_display": s.get_category_display(),
            "category_icon": s.category_icon,
            "state": s.state,
            "farmer_type": s.farmer_type,
            "short_description": s.short_description,
            "benefits_list": s.benefits_list,
            "eligibility_list": s.eligibility_list,
            "documents_list": s.documents_list,
            "steps_list": s.steps_list,
            "official_url": s.official_url,
            "helpline": s.helpline,
            "detail_url": s.get_absolute_url(),
        })

    return JsonResponse({
        "success": True,
        "count": len(data),
        "schemes": data,
    })


@require_http_methods(["GET", "POST"])
def check_eligibility_api(request):
    """
    API for calculating farmer eligibility score for all schemes.
    """
    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            payload = request.POST.dict()
    else:
        payload = request.GET.dict()

    state = payload.get("state", "All India")
    try:
        age = int(payload.get("age", 35))
    except (ValueError, TypeError):
        age = 35

    try:
        land_area = float(payload.get("land_area", 2.0))
    except (ValueError, TypeError):
        land_area = 2.0

    farmer_data = {
        "state": state,
        "age": age,
        "gender": payload.get("gender", "any"),
        "category": payload.get("social_category", "general"),
        "farmer_type": payload.get("farmer_type", "small"),
        "land_area": land_area,
        "annual_income": None,
        "crop": payload.get("crop", "wheat"),
        "season": payload.get("season", "kharif"),
    }

    schemes = GovernmentScheme.objects.filter(is_active=True)
    results = []

    for scheme in schemes:
        res = check_scheme_eligibility(scheme, farmer_data)
        if res.get("eligible"):
            results.append({
                "id": scheme.id,
                "title": scheme.title,
                "slug": scheme.slug,
                "category": scheme.category,
                "category_icon": scheme.category_icon,
                "score": res.get("score", 70),
                "reasons": res.get("reasons", []),
                "warnings": res.get("warnings", []),
                "official_url": scheme.official_url,
                "detail_url": scheme.get_absolute_url(),
                "short_description": scheme.short_description,
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return JsonResponse({
        "success": True,
        "count": len(results),
        "results": results,
    })