from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AlertPreference, AlertLog
from .forms import AlertPreferenceForm
from .services import NotificationService

@login_required
def alert_settings(request):
    preference, created = AlertPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = AlertPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alert preferences updated successfully.')
            return redirect('notifications:settings')
    else:
        form = AlertPreferenceForm(instance=preference)
        
    recent_logs = AlertLog.objects.filter(user=request.user).order_by('-sent_at')[:5]

    return render(request, 'notifications/alert_settings.html', {
        'form': form,
        'recent_logs': recent_logs
    })

@login_required
def test_alert(request):
    """View to test sending an alert based on user preferences."""
    if request.method == 'POST':
        # Check if the user has actually saved their phone number first
        preference = getattr(request.user, 'alert_preference', None)
        if not preference or not preference.phone_number:
            messages.error(request, "Please enter your Mobile Number and click 'Save Preferences' before testing alerts.")
            return redirect('notifications:settings')
        
        if not preference.whatsapp_enabled and not preference.sms_enabled:
            messages.error(request, "Please enable at least one alert method (WhatsApp or SMS) and click 'Save Preferences'.")
            return redirect('notifications:settings')

        alert_type = request.POST.get('alert_type', 'System Update')
        message = "This is a test alert from KisanSathi AI. Your notification preferences are working!"
        
        service = NotificationService()
        success = service.send_alert(request.user, alert_type, message)
        
        if success:
            messages.success(request, f"Test alert sent successfully for '{alert_type}'.")
        else:
            messages.error(request, "Failed to send alert. Check your phone number or notification preferences.")
            
    return redirect('notifications:settings')
