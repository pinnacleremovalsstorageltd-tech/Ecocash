from django.utils.deprecation import MiddlewareMixin
from .models import UserActivity, UserSession

class ActivityTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.user.last_activity = __import__('django.utils.timezone', fromlist=['now']).now()
            request.user.save(update_fields=['last_activity'])
        return None

class SecurityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and request.user.account_locked:
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, 'Your account is locked.')
            return redirect('accounts:login')
        return None
