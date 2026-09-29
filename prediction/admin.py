from django.contrib import admin
from .models import CropAnalysis

# Register CropAnalysis with Django Admin
try:
    admin.site.register(CropAnalysis)
except admin.sites.AlreadyRegistered:
    pass