from django.utils import timezone
from .models import UserActivity, UserNotification

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_client_location(request):
    return request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] if request.META.get('HTTP_X_FORWARDED_FOR') else ''

def log_user_activity(user, activity_type, description, metadata=None):
    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        metadata=metadata or {},
        ip_address=''
    )

def create_notification(user, type, title, message, link=None, priority=0, category=None):
    UserNotification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        link=link,
        priority=priority,
        category=category
    )

def send_verification_email(user):
    pass

def send_welcome_email(user):
    pass

def send_sms_code(user, code):
    if user and hasattr(user, 'phone_number') and user.phone_number:
        message = f"Your EcoCash verification code is {code}."
        print(f"[SMS] Sending to {user.phone_number}: {message}")
        # Integrate with a real SMS provider here, if available.
    else:
        print("[SMS] No phone number available for user, unable to send 2FA code.")

def generate_otp():
    import random
    return ''.join(str(random.randint(0, 9)) for _ in range(6))
