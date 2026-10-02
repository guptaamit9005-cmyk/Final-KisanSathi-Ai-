from django.db import models
from django.contrib.auth.models import User

class AlertPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alert_preference')
    phone_number = models.CharField(max_length=15, help_text="Phone number for SMS/WhatsApp alerts", blank=True, null=True)
    
    # The 5 automated alerts
    weather_alerts = models.BooleanField(default=True, help_text="Extreme weather warnings (rain, frost, etc.)")
    mandi_alerts = models.BooleanField(default=False, help_text="Price spikes for your crops")
    disease_alerts = models.BooleanField(default=True, help_text="Disease outbreak warnings in your district")
    irrigation_alerts = models.BooleanField(default=False, help_text="Irrigation & soil moisture reminders")
    scheme_alerts = models.BooleanField(default=True, help_text="Government scheme deadlines")

    # Preferred medium
    whatsapp_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Alert Preferences"

class AlertLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)
    message = models.TextField()
    sent_via = models.CharField(max_length=10, choices=[('SMS', 'SMS'), ('WhatsApp', 'WhatsApp')])
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Sent')

    def __str__(self):
        return f"{self.alert_type} to {self.user.username} via {self.sent_via}"
