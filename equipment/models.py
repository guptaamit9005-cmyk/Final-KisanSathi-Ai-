from django.db import models
from django.contrib.auth.models import User


class Equipment(models.Model):

    EQUIPMENT_TYPES = [
        ("tractor", "Tractor (ट्रैक्टर)"),
        ("rotavator", "Rotavator (रोटावेटर)"),
        ("seed_drill", "Seed Drill / Super Seeder (सुपर सीडर)"),
        ("sprayer", "Boom Sprayer (स्प्रेयर)"),
        ("drone", "Agri Drone Sprayer (कृषि ड्रोन)"),
        ("harvester", "Combine Harvester (कंबाइन हार्वेस्टर)"),
        ("leveler", "Laser Land Leveler (लेजर लेवलर)"),
        ("cultivator", "Cultivator / Plough (कल्टीवेटर)"),
        ("thresher", "Multi-Crop Thresher (थ्रेशर)"),
        ("pump", "Solar / Diesel Water Pump (पानी का पंप)"),
        ("other", "Other Implements (अन्य उपकरण)"),
    ]

    RENT_TYPES = [
        ("hour", "Per Hour"),
        ("day", "Per Day"),
        ("acre", "Per Acre"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("booked", "Booked"),
        ("maintenance", "Maintenance"),
        ("inactive", "Inactive"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="equipment_listings"
    )

    name = models.CharField(max_length=150)

    equipment_type = models.CharField(
        max_length=30,
        choices=EQUIPMENT_TYPES
    )

    brand = models.CharField(
        max_length=100,
        blank=True
    )

    model_number = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    location = models.CharField(
        max_length=200
    )

    district = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        default="Uttar Pradesh"
    )

    latitude = models.FloatField(
        null=True,
        blank=True,
        default=26.8467
    )

    longitude = models.FloatField(
        null=True,
        blank=True,
        default=80.9462
    )

    chc_hub_name = models.CharField(
        max_length=150,
        blank=True,
        default="Kisan CHC Hub"
    )

    rent_type = models.CharField(
        max_length=20,
        choices=RENT_TYPES,
        default="day"
    )

    rent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    acre_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    operator_available = models.BooleanField(
        default=False
    )

    delivery_available = models.BooleanField(
        default=False
    )

    fuel_included = models.BooleanField(
        default=False
    )

    contact_number = models.CharField(
        max_length=20,
        blank=True
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=4.8
    )

    total_trips = models.PositiveIntegerField(
        default=18
    )

    availability_note = models.CharField(
        max_length=150,
        blank=True,
        default="🟢 Live: Ready for instant dispatch"
    )

    image = models.ImageField(
        upload_to="equipment/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available"
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
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def rent_label(self):
        return dict(self.RENT_TYPES).get(
            self.rent_type,
            self.rent_type
        )

    @property
    def display_hourly_rate(self):
        if self.hourly_rate:
            return self.hourly_rate
        if self.rent_type == "hour":
            return self.rent_amount
        return round(float(self.rent_amount) / 8, 2)

    @property
    def display_acre_rate(self):
        if self.acre_rate:
            return self.acre_rate
        if self.rent_type == "acre":
            return self.rent_amount
        return round(float(self.display_hourly_rate) * 1.4, 2)


class EquipmentBooking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="equipment_bookings"
    )

    start_date = models.DateField()

    end_date = models.DateField()

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1
    )

    message = models.TextField(
        blank=True
    )

    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
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

    def __str__(self):
        return (
            f"{self.farmer.username} - "
            f"{self.equipment.name}"
        )