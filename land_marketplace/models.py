from decimal import Decimal

from django.conf import settings
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.db.models import Q


class Land(models.Model):

    LAND_TYPES = [
        ("agricultural", "Agricultural"),
        ("orchard", "Orchard"),
        ("greenhouse", "Greenhouse"),
        ("mixed", "Mixed Farming"),
    ]

    LISTING_TYPES = [
        ("rent", "Rent"),
        ("share", "Share"),
        ("lease", "Lease"),
    ]

    WATER_SOURCES = [
        ("none", "No Water Source"),
        ("borewell", "Borewell"),
        ("canal", "Canal"),
        ("tube_well", "Tube Well"),
        ("rainwater", "Rainwater"),
        ("multiple", "Multiple Sources"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("occupied", "Occupied"),
        ("closed", "Closed"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="land_marketplace_listings",
    )

    title = models.CharField(
        max_length=180
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )

    land_type = models.CharField(
        max_length=30,
        choices=LAND_TYPES,
        default="agricultural"
    )

    listing_type = models.CharField(
        max_length=20,
        choices=LISTING_TYPES,
        default="share"
    )

    # Location
    village = models.CharField(
        max_length=120
    )

    district = models.CharField(
        max_length=120
    )

    state = models.CharField(
        max_length=120
    )

    pincode = models.CharField(
        max_length=10,
        blank=True
    )

    # Do not expose exact coordinates publicly.
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Land information
    total_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    available_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    soil_type = models.CharField(
        max_length=100,
        blank=True
    )

    soil_description = models.TextField(
        blank=True
    )

    suitable_crops = models.CharField(
        max_length=400,
        blank=True
    )

    water_source = models.CharField(
        max_length=30,
        choices=WATER_SOURCES,
        default="none"
    )

    electricity_available = models.BooleanField(
        default=False
    )

    road_access = models.BooleanField(
        default=True
    )

    # Commercial
    rent_per_acre_month = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0"))
        ]
    )

    security_deposit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    minimum_duration_months = models.PositiveIntegerField(
        default=1
    )

    maximum_duration_months = models.PositiveIntegerField(
        default=60
    )

    # Content
    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="land_marketplace/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    is_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-is_verified", "-created_at"]

        indexes = [
            models.Index(
                fields=["state", "district"]
            ),
            models.Index(
                fields=["status", "listing_type"]
            ),
            models.Index(
                fields=["available_area"]
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=Q(
                    available_area__lte=models.F("total_area")
                ),
                name="available_area_lte_total_area"
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def location(self):
        return (
            f"{self.village}, "
            f"{self.district}, "
            f"{self.state}"
        )

    @property
    def monthly_price_for_full_area(self):
        return (
            self.rent_per_acre_month
            * self.available_area
        )


class LandImage(models.Model):

    land = models.ForeignKey(
        Land,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="land_marketplace/gallery/"
    )

    is_primary = models.BooleanField(
        default=False
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )


class LandRequest(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("owner_review", "Owner Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    land = models.ForeignKey(
        Land,
        on_delete=models.CASCADE,
        related_name="requests"
    )

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="land_requests"
    )

    requested_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    duration_months = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    proposed_start_date = models.DateField()

    message = models.TextField(
        blank=True
    )

    calculated_rent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    security_deposit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    total_estimated_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0")
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending"
    )

    owner_response = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "land",
                    "requester",
                ],
                condition=Q(
                    status__in=[
                        "pending",
                        "owner_review",
                        "approved",
                    ]
                ),
                name="one_active_request_per_farmer_land"
            )
        ]

    def __str__(self):
        return (
            f"{self.requester.username} → "
            f"{self.land.title}"
        )

    def calculate_cost(self):

        self.calculated_rent = (
            self.land.rent_per_acre_month
            * self.requested_area
            * self.duration_months
        )

        self.security_deposit = (
            self.land.security_deposit
        )

        self.total_estimated_cost = (
            self.calculated_rent
            + self.security_deposit
        )

        return self.total_estimated_cost