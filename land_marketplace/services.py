from decimal import Decimal

from django.db import transaction

from .models import Land, LandRequest


class LandMarketplaceService:

    @staticmethod
    def calculate_request_cost(
        land,
        area,
        duration_months
    ):

        area = Decimal(str(area))
        duration = Decimal(str(duration_months))

        rent = (
            land.rent_per_acre_month
            * area
            * duration
        )

        deposit = land.security_deposit

        total = rent + deposit

        return {
            "rent": rent,
            "deposit": deposit,
            "total": total,
        }


    @staticmethod
    @transaction.atomic
    def create_request(
        *,
        land,
        requester,
        area,
        duration_months,
        proposed_start_date,
        message=""
    ):

        if land.owner_id == requester.id:

            raise ValueError(
                "You cannot request your own land."
            )

        if land.status != "active":

            raise ValueError(
                "This land is not currently available."
            )

        area = Decimal(str(area))

        if area > land.available_area:

            raise ValueError(
                "Requested area is not available."
            )

        costs = (
            LandMarketplaceService
            .calculate_request_cost(
                land,
                area,
                duration_months
            )
        )

        request = LandRequest.objects.create(
            land=land,
            requester=requester,
            requested_area=area,
            duration_months=duration_months,
            proposed_start_date=proposed_start_date,
            message=message,
            calculated_rent=costs["rent"],
            security_deposit=costs["deposit"],
            total_estimated_cost=costs["total"],
            status="owner_review",
        )

        return request


    @staticmethod
    @transaction.atomic
    def approve_request(
        *,
        land_request,
        owner
    ):

        if land_request.land.owner_id != owner.id:

            raise PermissionError(
                "You are not the land owner."
            )

        if land_request.status != "owner_review":

            raise ValueError(
                "This request cannot be approved."
            )

        land = (
            Land.objects
            .select_for_update()
            .get(
                pk=land_request.land_id
            )
        )

        if (
            land_request.requested_area
            > land.available_area
        ):

            raise ValueError(
                "Not enough land is available."
            )

        land.available_area -= (
            land_request.requested_area
        )

        if land.available_area <= 0:

            land.available_area = Decimal("0")
            land.status = "occupied"

        land.save(
            update_fields=[
                "available_area",
                "status",
                "updated_at",
            ]
        )

        land_request.status = "approved"

        land_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return land_request


    @staticmethod
    @transaction.atomic
    def reject_request(
        *,
        land_request,
        owner,
        response=""
    ):

        if land_request.land.owner_id != owner.id:

            raise PermissionError(
                "You are not the land owner."
            )

        if land_request.status not in [
            "owner_review",
            "pending",
        ]:

            raise ValueError(
                "This request cannot be rejected."
            )

        land_request.status = "rejected"
        land_request.owner_response = response

        land_request.save(
            update_fields=[
                "status",
                "owner_response",
                "updated_at",
            ]
        )

        return land_request