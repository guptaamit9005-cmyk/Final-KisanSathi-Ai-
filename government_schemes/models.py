from django.db import models


class GovernmentScheme(models.Model):

    CATEGORY_CHOICES = [
        ("income", "Income Support"),
        ("insurance", "Crop Insurance"),
        ("credit", "Credit"),
        ("subsidy", "Subsidy"),
        ("equipment", "Farm Equipment"),
        ("irrigation", "Irrigation"),
        ("education", "Education"),
        ("other", "Other"),
    ]

    GENDER_CHOICES = [
        ("any", "Any"),
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    FARMER_TYPE_CHOICES = [
        ("any", "Any"),
        ("small", "Small Farmer"),
        ("marginal", "Marginal Farmer"),
        ("tenant", "Tenant Farmer"),
        ("landless", "Landless Farmer"),
        ("all", "All Farmers"),
    ]

    title = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    short_description = models.CharField(
        max_length=500,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="other"
    )
    state = models.CharField(
        max_length=100,
        default="All India"
    )

    district = models.CharField(
        max_length=100,
        blank=True
    )
    min_age = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    max_age = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default="any"
    )

    farmer_type = models.CharField(
        max_length=30,
        choices=FARMER_TYPE_CHOICES,
        default="any"
    )

    min_land_area = models.FloatField(
        null=True,
        blank=True,
        help_text="Minimum land area in acres"
    )

    max_land_area = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum land area in acres"
    )

    max_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # ------------------------------------------------
    # CROP
    # ------------------------------------------------

    crops = models.JSONField(
        default=list,
        blank=True
    )

    seasons = models.JSONField(
        default=list,
        blank=True
    )

    # ------------------------------------------------
    # BENEFITS
    # ------------------------------------------------

    benefits = models.TextField(
        blank=True
    )

    eligibility = models.TextField(
        blank=True
    )

    documents = models.TextField(
        blank=True
    )

    application_process = models.TextField(
        blank=True
    )

    # ------------------------------------------------
    # CURRENT AVAILABILITY
    # ------------------------------------------------

    valid_from = models.DateField(
        null=True,
        blank=True
    )

    valid_until = models.DateField(
        null=True,
        blank=True
    )

    application_deadline = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    # ------------------------------------------------
    # OFFICIAL SOURCE
    # ------------------------------------------------

    official_url = models.URLField(
        blank=True
    )

    source_url = models.URLField(
        blank=True
    )

    helpline = models.CharField(
        max_length=100,
        blank=True
    )

    # ------------------------------------------------
    # VERIFICATION
    # ------------------------------------------------

    last_verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    verification_source = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title