import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from .ml_model.predictor import predict_disease
from .ml_model.disease_data import DISEASE_INFO


def predict_view(request):
    """
    GET  -> shows the empty upload/camera form.
    POST -> saves the uploaded image, runs the AI model, and renders
            the same page with the prediction + treatment info filled in.
    """
    context = {}

    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]

        upload_dir = os.path.join(settings.MEDIA_ROOT, "leaf_uploads")
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(image_file.name, image_file)
        file_path = fs.path(filename)
        file_url = os.path.join(settings.MEDIA_URL, "leaf_uploads", filename)

        try:
            label, confidence = predict_disease(file_path)

            info = DISEASE_INFO.get(label)
            if info is None:
                info = {
                    "name": label.replace("_", " ").replace("__", " — "),
                    "status": "infected",
                    "severity": "Unknown",
                    "spread": "Unknown",
                    "treatment": ["No treatment data available for this class yet."],
                }

            context["result"] = {
                "name": info["name"],
                "status": info["status"],          # "healthy" or "infected"
                "severity": info["severity"],
                "spread": info["spread"],
                "treatment": info["treatment"],
                "confidence": confidence,           # e.g. 92.4
            }
            context["uploaded_image_url"] = file_url

        except FileNotFoundError as e:
            context["error"] = str(e)
        except Exception as e:
            context["error"] = f"Prediction failed: {e}"

    return render(request, "prediction/predict.html", context)