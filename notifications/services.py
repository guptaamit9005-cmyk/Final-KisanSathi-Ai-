from .models import AlertPreference, AlertLog
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Mock service to simulate sending WhatsApp and SMS notifications.
    In production, this would integrate with Twilio, AWS SNS, etc.
    """
    
    def send_alert(self, user, alert_type, message):
        try:
            preference = AlertPreference.objects.get(user=user)
        except AlertPreference.DoesNotExist:
            return False

        if not preference.phone_number:
            return False

        # Determine which channels are active
        channels = []
        if preference.whatsapp_enabled:
            channels.append('WhatsApp')
        if preference.sms_enabled:
            channels.append('SMS')

        if not channels:
            return False

        success = False
        
        for channel in channels:
            # Here you would call your API, e.g. Twilio API
            logger.info(f"Sending {channel} to {preference.phone_number}: [{alert_type}] {message}")
            
            # Log the successful mock send
            AlertLog.objects.create(
                user=user,
                alert_type=alert_type,
                message=message,
                sent_via=channel,
                status='Sent'
            )
            success = True

        return success
