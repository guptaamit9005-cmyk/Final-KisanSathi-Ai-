from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    LandListingForm,
    LandRequestForm,
    LandSearchForm,
)

from .models import (
    Land,
    LandRequest,
)

from .services import (
    LandMarketplaceService,
)


@login_required(login_url="accounts:login")
def land_list(request):

    form = LandSearchForm(request.GET)

    lands = (
        Land.objects
        .filter(status="active")
        .select_related("owner")
        .prefetch_related("images")
    )

    if form.is_valid():

        q = form.cleaned_data.get("q")
        district = form.cleaned_data.get("district")
        crop = form.cleaned_data.get("crop")
        land_type = form.cleaned_data.get("land_type")
        listing_type = form.cleaned_data.get("listing_type")
        min_area = form.cleaned_data.get("min_area")
        max_price = form.cleaned_data.get("max_price")

        if q:

            lands = lands.filter(
                Q(title__icontains=q)
                |
                Q(village__icontains=q)
                |
                Q(district__icontains=q)
                |
                Q(suitable_crops__icontains=q)
                |
                Q(soil_type__icontains=q)
            )

        if district:

            lands = lands.filter(
                district__icontains=district
            )

        if crop:

            lands = lands.filter(
                suitable_crops__icontains=crop
            )

        if land_type:

            lands = lands.filter(
                land_type=land_type
            )

        if listing_type:

            lands = lands.filter(
                listing_type=listing_type
            )

        if min_area:

            lands = lands.filter(
                available_area__gte=min_area
            )

        if max_price:

            lands = lands.filter(
                rent_per_acre_month__lte=max_price
            )

    paginator = Paginator(
        lands,
        12
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        "land_marketplace/list.html",
        {
            "lands": page_obj,
            "search_form": form,
            "page_obj": page_obj,
        }
    )


@login_required(login_url="accounts:login")
def land_detail(
    request,
    land_id
):

    land = get_object_or_404(
        Land.objects
        .select_related("owner")
        .prefetch_related("images"),
        id=land_id,
        status="active",
    )

    form = LandRequestForm(
        land=land
    )

    if request.method == "POST":

        form = LandRequestForm(
            request.POST,
            land=land
        )

        if form.is_valid():

            try:

                LandMarketplaceService.create_request(
                    land=land,
                    requester=request.user,
                    area=form.cleaned_data[
                        "requested_area"
                    ],
                    duration_months=form.cleaned_data[
                        "duration_months"
                    ],
                    proposed_start_date=form.cleaned_data[
                        "proposed_start_date"
                    ],
                    message=form.cleaned_data[
                        "message"
                    ],
                )

                return redirect(
                    "land_marketplace:my_requests"
                )

            except ValueError as exc:

                form.add_error(
                    None,
                    str(exc)
                )

    return render(
        request,
        "land_marketplace/detail.html",
        {
            "land": land,
            "form": form,
        }
    )


@login_required(login_url="accounts:login")
def create_land(request):

    if request.method == "POST":

        form = LandListingForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            land = form.save(
                commit=False
            )

            land.owner = request.user
            land.status = "active"

            land.save()

            return redirect(
                "land_marketplace:my_land"
            )

    else:

        form = LandListingForm()

    return render(
        request,
        "land_marketplace/create.html",
        {
            "form": form
        }
    )


@login_required(login_url="accounts:login")
def my_land(request):

    lands = (
        Land.objects
        .filter(owner=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "land_marketplace/my_land.html",
        {
            "lands": lands
        }
    )


@login_required(login_url="accounts:login")
def my_requests(request):

    requests = (
        LandRequest.objects
        .filter(
            requester=request.user
        )
        .select_related("land")
        .order_by("-created_at")
    )

    return render(
        request,
        "land_marketplace/my_requests.html",
        {
            "requests": requests
        }
    )


@login_required(login_url="accounts:login")
def owner_requests(request):

    requests = (
        LandRequest.objects
        .filter(
            land__owner=request.user
        )
        .select_related(
            "land",
            "requester"
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "land_marketplace/owner_requests.html",
        {
            "requests": requests
        }
    )


@login_required(login_url="accounts:login")
def approve_request(
    request,
    request_id
):

    if request.method != "POST":

        return redirect(
            "land_marketplace:owner_requests"
        )

    land_request = get_object_or_404(
        LandRequest,
        id=request_id,
        land__owner=request.user
    )

    try:

        LandMarketplaceService.approve_request(
            land_request=land_request,
            owner=request.user
        )

    except (
        ValueError,
        PermissionError
    ):

        pass

    return redirect(
        "land_marketplace:owner_requests"
    )


@login_required(login_url="accounts:login")
def reject_request(
    request,
    request_id
):

    if request.method != "POST":

        return redirect(
            "land_marketplace:owner_requests"
        )

    land_request = get_object_or_404(
        LandRequest,
        id=request_id,
        land__owner=request.user
    )

    LandMarketplaceService.reject_request(
        land_request=land_request,
        owner=request.user,
        response=request.POST.get(
            "response",
            ""
        )
    )

    return redirect(
        "land_marketplace:owner_requests"
    )


@login_required(login_url="accounts:login")
def calculate_cost_api(
    request,
    land_id
):

    land = get_object_or_404(
        Land,
        id=land_id,
        status="active"
    )

    try:

        area = float(
            request.GET.get(
                "area",
                0
            )
        )

        duration = int(
            request.GET.get(
                "duration",
                1
            )
        )

        costs = (
            LandMarketplaceService
            .calculate_request_cost(
                land,
                area,
                duration
            )
        )

        return JsonResponse(
            {
                "success": True,
                "rent": str(
                    costs["rent"]
                ),
                "deposit": str(
                    costs["deposit"]
                ),
                "total": str(
                    costs["total"]
                ),
            }
        )

    except (
        ValueError,
        TypeError
    ):

        return JsonResponse(
            {
                "success": False,
                "message":
                    "Invalid area or duration."
            },
            status=400
        )