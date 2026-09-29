# app-level urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("prediction/", views.predict_view, name="predict"),
]

# In your project-level settings.py, also make sure media is configured:
#
#   MEDIA_URL = "/media/"
#   MEDIA_ROOT = BASE_DIR / "media"
#
# And in your project-level urls.py (only needed while DEBUG=True):
#
#   from django.conf import settings
#   from django.conf.urls.static import static
#
#   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)