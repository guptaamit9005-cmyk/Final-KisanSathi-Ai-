from django import forms
from .models import SoilAnalysis


class SoilAnalysisForm(forms.ModelForm):
    class Meta:
        model = SoilAnalysis
        fields = [
            "farm_name",
            "location",
            "target_crop",
            "nitrogen",
            "phosphorus",
            "potassium",
            "temperature",
            "humidity",
            "ph",
            "rainfall",
            "organic_carbon",
            "electrical_conductivity",
            "soil_texture",
        ]

        widgets = {
            "farm_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. North Field",
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Village, district",
            }),
            "target_crop": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Optional: crop you plan to grow",
            }),
            "nitrogen": forms.NumberInput(attrs={
                "class": "form-control", "step": "any", "min": "0",
            }),
            "phosphorus": forms.NumberInput(attrs={
                "class": "form-control", "step": "any", "min": "0",
            }),
            "potassium": forms.NumberInput(attrs={
                "class": "form-control", "step": "any", "min": "0",
            }),
            "temperature": forms.NumberInput(attrs={
                "class": "form-control", "step": "any",
            }),
            "humidity": forms.NumberInput(attrs={
                "class": "form-control", "step": "any", "min": "0", "max": "100",
            }),
            "ph": forms.NumberInput(attrs={
                "class": "form-control", "step": "any", "min": "0", "max": "14",
            }),
            "rainfall": forms.NumberInput(attrs={
                "class": "form-control", "step": "any", "min": "0",
            }),
            "organic_carbon": forms.NumberInput(attrs={
                "class": "form-control", "step": "any", "min": "0",
                "placeholder": "Optional",
            }),
            "electrical_conductivity": forms.NumberInput(attrs={
                "class": "form-control", "step": "any", "min": "0",
                "placeholder": "Optional; enter lab value and unit",
            }),
            "soil_texture": forms.Select(attrs={"class": "form-control"}),
        }

        labels = {
            "nitrogen": "Nitrogen (N) — enter soil-test value",
            "phosphorus": "Phosphorus (P) — enter soil-test value",
            "potassium": "Potassium (K) — enter soil-test value",
            "temperature": "Temperature (°C)",
            "humidity": "Humidity (%)",
            "ph": "Soil pH",
            "rainfall": "Rainfall (mm)",
            "organic_carbon": "Organic carbon (%) — optional",
            "electrical_conductivity": "Electrical conductivity (EC) — optional",
        }

    def clean(self):
        cleaned = super().clean()

        for field in [
            "nitrogen", "phosphorus", "potassium",
            "rainfall", "organic_carbon", "electrical_conductivity",
        ]:
            value = cleaned.get(field)
            if value is not None and value < 0:
                self.add_error(field, "Value cannot be negative.")

        ph = cleaned.get("ph")
        if ph is not None and not 0 <= ph <= 14:
            self.add_error("ph", "pH must be between 0 and 14.")

        humidity = cleaned.get("humidity")
        if humidity is not None and not 0 <= humidity <= 100:
            self.add_error("humidity", "Humidity must be between 0 and 100.")

        return cleaned