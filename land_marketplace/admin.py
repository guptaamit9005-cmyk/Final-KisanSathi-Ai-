from django.contrib import admin

from .models import (
    Land,
    LandImage,
    LandRequest,
)


@admin.register(Land)
class LandAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "owner",
        "district",
        "state",
        "land_type",
        "listing_type",
        "available_area",
        "rent_per_acre_month",
        "is_verified",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "land_type",
        "listing_type",
        "water_source",
        "is_verified",
        "electricity_available",
        "road_access",
        "state",
    )

    search_fields = (
        "title",
        "village",
        "district",
        "state",
        "suitable_crops",
        "owner__username",
        "owner__email",
    )

    readonly_fields = (
        "slug",
        "created_at",
        "updated_at",
    )

    list_per_page = 25

    ordering = (
        "-is_verified",
        "-created_at",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "owner",
                    "title",
                    "land_type",
                    "listing_type",
                    "description",
                )
            },
        ),

        (
            "Location",
            {
                "fields": (
                    "village",
                    "district",
                    "state",
                    "pincode",
                    "latitude",
                    "longitude",
                )
            },
        ),

        (
            "Land Details",
            {
                "fields": (
                    "total_area",
                    "available_area",
                    "soil_type",
                    "soil_description",
                    "suitable_crops",
                    "water_source",
                    "electricity_available",
                    "road_access",
                )
            },
        ),

        (
            "Commercial Details",
            {
                "fields": (
                    "rent_per_acre_month",
                    "security_deposit",
                    "minimum_duration_months",
                    "maximum_duration_months",
                )
            },
        ),

        (
            "Marketplace Status",
            {
                "fields": (
                    "status",
                    "is_verified",
                )
            },
        ),

        (
            "System",
            {
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                    "image",
                )
            },
        ),
    )


@admin.register(LandImage)
class LandImageAdmin(admin.ModelAdmin):

    list_display = (
        "land",
        "is_primary",
        "uploaded_at",
    )

    list_filter = (
        "is_primary",
        "uploaded_at",
    )

    search_fields = (
        "land__title",
        "land__district",
        "land__village",
    )


@admin.register(LandRequest)
class LandRequestAdmin(admin.ModelAdmin):

    list_display = (
        "land",
        "requester",
        "requested_area",
        "duration_months",
        "calculated_rent",
        "total_estimated_cost",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "land__title",
        "requester__username",
        "requester__email",
    )

    readonly_fields = (
        "calculated_rent",
        "security_deposit",
        "total_estimated_cost",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )