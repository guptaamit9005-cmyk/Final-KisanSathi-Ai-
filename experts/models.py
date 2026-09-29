from django.db import models


class Expert(models.Model):

    EXPERT_TYPES = [
        ("scientist", "Agricultural Scientist"),
        ("researcher", "Agricultural Researcher"),
        ("farmer", "Experienced Farmer"),
        ("organization", "Agricultural Organization"),
        ("company", "Agricultural Company"),
        ("university", "Agricultural University"),
        ("specialist", "Agriculture Specialist"),
    ]

    VERIFICATION_STATUS = [
        ("verified", "Verified"),
        ("pending", "Pending Verification"),
    ]

    name = models.CharField(
        max_length=200
    )

    expert_type = models.CharField(
        max_length=30,
        choices=EXPERT_TYPES
    )

    organization = models.CharField(
        max_length=250,
        blank=True,
        null=True
    )

    designation = models.CharField(
        max_length=250,
        blank=True,
        null=True
    )

    specialization = models.CharField(
        max_length=300
    )

    crops = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Example: Rice, Wheat, Tomato"
    )

    location = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    languages = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="Example: Hindi, English, Bengali"
    )

    experience_years = models.PositiveIntegerField(
        default=0
    )

    about = models.TextField(
        blank=True,
        null=True
    )

    profile_image = models.ImageField(
        upload_to="experts/",
        blank=True,
        null=True
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    official_profile = models.URLField(
        blank=True,
        null=True
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default="pending"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return self.name