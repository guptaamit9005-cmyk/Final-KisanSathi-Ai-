from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    EquipmentBookingForm,
    EquipmentForm,
    EquipmentSearchForm,
)

from .models import Equipment, EquipmentBooking


# ============================================================
# EQUIPMENT HOME
# ============================================================

@login_required(login_url="accounts:login")
def equipment_home(request):

    form = EquipmentSearchForm(request.GET or None)

    equipment = Equipment.objects.filter(
        status="available"
    ).select_related(
        "owner"
    )

    if form.is_valid():

        q = form.cleaned_data.get("q")
        equipment_type = form.cleaned_data.get("equipment_type")
        district = form.cleaned_data.get("district")
        rent_type = form.cleaned_data.get("rent_type")

        if q:
            equipment = equipment.filter(
                Q(name__icontains=q)
                | Q(brand__icontains=q)
                | Q(description__icontains=q)
                | Q(location__icontains=q)
            )

        if equipment_type:
            equipment = equipment.filter(
                equipment_type=equipment_type
            )

        if district:
            equipment = equipment.filter(
                district__icontains=district
            )

        if rent_type:
            equipment = equipment.filter(
                rent_type=rent_type
            )

    all_available = Equipment.objects.filter(status="available")
    total_count = all_available.count()
    tractors_count = all_available.filter(equipment_type="tractor").count()
    harvesters_count = all_available.filter(equipment_type="harvester").count()
    drones_count = all_available.filter(equipment_type="drone").count()
    verified_count = all_available.filter(is_verified=True).count()
    with_operator_count = all_available.filter(operator_available=True).count()
    with_delivery_count = all_available.filter(delivery_available=True).count()

    context = {
        "equipment": equipment,
        "form": form,
        "total_count": total_count,
        "tractors_count": tractors_count,
        "harvesters_count": harvesters_count,
        "drones_count": drones_count,
        "verified_count": verified_count,
        "with_operator_count": with_operator_count,
        "with_delivery_count": with_delivery_count,
    }

    return render(
        request,
        "equipment/equipment.html",
        context
    )


# ============================================================
# EQUIPMENT DETAIL
# ============================================================

@login_required(login_url="accounts:login")
def equipment_detail(request, equipment_id):

    equipment = get_object_or_404(
        Equipment.objects.select_related("owner"),
        id=equipment_id
    )

    booking_form = EquipmentBookingForm()

    return render(
        request,
        "equipment/detail.html",
        {
            "equipment": equipment,
            "booking_form": booking_form,
        }
    )


# ============================================================
# ADD EQUIPMENT
# ============================================================

@login_required(login_url="accounts:login")
def add_equipment(request):

    if request.method == "POST":

        form = EquipmentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            equipment = form.save(
                commit=False
            )

            equipment.owner = request.user
            equipment.status = "available"

            equipment.save()

            return redirect(
                "equipment:home"
            )

    else:

        form = EquipmentForm()

    return render(
        request,
        "equipment/add.html",
        {
            "form": form
        }
    )


# ============================================================
# BOOK EQUIPMENT
# ============================================================

@login_required(login_url="accounts:login")
def book_equipment(
    request,
    equipment_id
):

    equipment = get_object_or_404(
        Equipment,
        id=equipment_id
    )

    # Equipment must be available
    if equipment.status != "available":

        return render(
            request,
            "equipment/detail.html",
            {
                "equipment": equipment,
                "booking_form": EquipmentBookingForm(),
                "error_message": (
                    "This equipment is currently "
                    "not available for booking."
                ),
            }
        )

    # Owner cannot book their own equipment
    if equipment.owner == request.user:

        return render(
            request,
            "equipment/detail.html",
            {
                "equipment": equipment,
                "booking_form": EquipmentBookingForm(),
                "error_message": (
                    "You cannot book your own equipment."
                ),
            }
        )

    if request.method != "POST":

        return redirect(
            "equipment:detail",
            equipment_id=equipment.id
        )

    form = EquipmentBookingForm(
        request.POST
    )

    if form.is_valid():

        booking = form.save(
            commit=False
        )

        booking.equipment = equipment
        booking.farmer = request.user

        # ----------------------------------------------------
        # DATE CALCULATION
        # ----------------------------------------------------

        start_date = booking.start_date
        end_date = booking.end_date

        days = (
            end_date - start_date
        ).days + 1

        if days < 1:

            form.add_error(
                "end_date",
                "End date must be after or equal to start date."
            )

            return render(
                request,
                "equipment/detail.html",
                {
                    "equipment": equipment,
                    "booking_form": form,
                }
            )

        # ----------------------------------------------------
        # COST CALCULATION
        # ----------------------------------------------------

        rent_amount = equipment.rent_amount
        quantity = booking.quantity

        if equipment.rent_type == "day":

            estimated_cost = (
                rent_amount
                * Decimal(days)
                * quantity
            )

        elif equipment.rent_type == "acre":

            estimated_cost = (
                rent_amount
                * quantity
            )

        elif equipment.rent_type == "hour":

            # Current booking form doesn't have
            # a separate hours field.
            #
            # Therefore quantity is treated as
            # the number of rental hours.

            estimated_cost = (
                rent_amount
                * quantity
            )

        else:

            estimated_cost = (
                rent_amount
                * Decimal(days)
                * quantity
            )

        booking.estimated_cost = estimated_cost

        booking.save()

        return redirect(
            "equipment:my_bookings"
        )

    return render(
        request,
        "equipment/detail.html",
        {
            "equipment": equipment,
            "booking_form": form,
        }
    )


# ============================================================
# MY BOOKINGS
# ============================================================

@login_required(login_url="accounts:login")
def my_bookings(request):

    bookings = (
        EquipmentBooking.objects
        .filter(
            farmer=request.user
        )
        .select_related(
            "equipment",
            "equipment__owner"
        )
        .order_by(
            "-created_at"
        )
    )

    pending_count = bookings.filter(
        status="pending"
    ).count()

    approved_count = bookings.filter(
        status="approved"
    ).count()

    completed_count = bookings.filter(
        status="completed"
    ).count()

    rejected_count = bookings.filter(
        status="rejected"
    ).count()

    context = {
        "bookings": bookings,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "completed_count": completed_count,
        "rejected_count": rejected_count,
    }

    return render(
        request,
        "equipment/my_bookings.html",
        context
    )


# ============================================================
# MY EQUIPMENT
# ============================================================

@login_required(login_url="accounts:login")
def my_equipment(request):

    equipment = (
        Equipment.objects
        .filter(
            owner=request.user
        )
        .order_by(
            "-created_at"
        )
    )

    context = {
        "equipment": equipment,
    }

    return render(
        request,
        "equipment/my_equipment.html",
        context
    )


# ============================================================
# OWNER BOOKINGS
# ============================================================

@login_required(login_url="accounts:login")
def owner_bookings(request):

    bookings = (
        EquipmentBooking.objects
        .filter(
            equipment__owner=request.user
        )
        .select_related(
            "equipment",
            "farmer"
        )
        .order_by(
            "-created_at"
        )
    )

    pending_count = bookings.filter(
        status="pending"
    ).count()

    approved_count = bookings.filter(
        status="approved"
    ).count()

    rejected_count = bookings.filter(
        status="rejected"
    ).count()

    context = {
        "bookings": bookings,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
    }

    return render(
        request,
        "equipment/owner_bookings.html",
        context
    )


# ============================================================
# APPROVE BOOKING
# ============================================================

@login_required(login_url="accounts:login")
def approve_booking(
    request,
    booking_id
):

    booking = get_object_or_404(
        EquipmentBooking.objects.select_related(
            "equipment",
            "farmer"
        ),
        id=booking_id,
        equipment__owner=request.user
    )

    if request.method == "POST":

        # Only pending bookings can be approved
        if booking.status == "pending":

            booking.status = "approved"

            booking.owner_response = (
                request.POST.get(
                    "response",
                    ""
                ).strip()
            )

            booking.save()

    return redirect(
        "equipment:owner_bookings"
    )


# ============================================================
# REJECT BOOKING
# ============================================================

@login_required(login_url="accounts:login")
def reject_booking(
    request,
    booking_id
):

    booking = get_object_or_404(
        EquipmentBooking.objects.select_related(
            "equipment",
            "farmer"
        ),
        id=booking_id,
        equipment__owner=request.user
    )

    if request.method == "POST":

        # Only pending bookings can be rejected
        if booking.status == "pending":

            booking.status = "rejected"

            booking.owner_response = (
                request.POST.get(
                    "response",
                    ""
                ).strip()
            )

            booking.save()

    return redirect(
        "equipment:owner_bookings"
    )