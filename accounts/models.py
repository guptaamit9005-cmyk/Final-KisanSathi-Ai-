from django.db import models
from django.contrib.auth.models import User


class FarmerProfile(models.Model):

    ROLE_CHOICES = (
        ("Farmer", "Farmer"),
        ("Expert", "Expert"),
        ("Admin", "Admin"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="Farmer"
    )

    phone = models.CharField(max_length=15)

    village = models.CharField(max_length=100)

    district = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username