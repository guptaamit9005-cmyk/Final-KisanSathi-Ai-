from django import forms
from .models import AlertPreference

class AlertPreferenceForm(forms.ModelForm):
    class Meta:
        model = AlertPreference
        fields = [
            'phone_number',
            'weather_alerts',
            'mandi_alerts',
            'disease_alerts',
            'irrigation_alerts',
            'scheme_alerts',
            'whatsapp_enabled',
            'sms_enabled'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 9876543210'}),
        }
