from django.utils.translation import gettext_lazy as _

def notification_count(request):
    if request.user.is_authenticated:
        from .models import UserNotification
        count = UserNotification.objects.filter(user=request.user, is_read=False).count()
        return {'notification_count': count}
    return {'notification_count': 0}
