from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from core.models import Address, Document
import uuid

class User(AbstractUser):
    USER_TYPES = [
        ('partner', 'Partner'),
        ('agent', 'Agent'),
        ('merchant', 'Merchant'),
        ('developer', 'Developer'),
        ('admin', 'Administrator'),
    ]
    ACCOUNT_STATUS = [
        ('pending', 'Pending Verification'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked')
    ]
    ID_TYPES = [
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
        ('business_reg', 'Business Registration')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='partner')
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default='pending')
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)
    id_type = models.CharField(max_length=20, choices=ID_TYPES, blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    id_expiry_date = models.DateField(null=True, blank=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    business_registration_number = models.CharField(max_length=50, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    tax_clearance_number = models.CharField(max_length=50, blank=True, null=True)
    industry = models.CharField(max_length=50, blank=True, null=True)
    years_in_business = models.IntegerField(null=True, blank=True)
    employee_count = models.IntegerField(null=True, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0)
    business_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_users')
    home_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='home_users')
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    security_question = models.CharField(max_length=200, blank=True, null=True)
    security_answer = models.CharField(max_length=200, blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=100, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_location = models.CharField(max_length=255, blank=True, null=True)
    login_count = models.IntegerField(default=0)
    login_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_identity_verified = models.BooleanField(default=False)
    is_business_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    verification_token_expires = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    terms_version = models.CharField(max_length=10, blank=True, null=True)
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='Africa/Harare')
    notification_preferences = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'auth_user'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['user_type']),
            models.Index(fields=['account_status']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def is_active_account(self):
        return self.account_status == 'active'

    def is_verified(self):
        return all([
            self.is_email_verified,
            self.is_identity_verified,
            self.is_business_verified
        ])

    def lock_account(self, duration_minutes=30):
        self.account_locked = True
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save()

    def unlock_account(self):
        self.account_locked = False
        self.locked_until = None
        self.login_attempts = 0
        self.save()

    def track_login(self, request=None):
        self.login_count += 1
        self.last_login = timezone.now()
        self.last_activity = timezone.now()
        if request is not None:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                self.last_login_ip = x_forwarded_for.split(',')[0].strip()
            else:
                self.last_login_ip = request.META.get('REMOTE_ADDR')
        self.save(update_fields=['login_count', 'last_login', 'last_login_ip', 'last_activity'])

    def get_profile_completion_percentage(self):
        required_fields = [
            self.first_name, self.last_name, self.email, self.phone_number,
            self.date_of_birth, self.id_type, self.id_number, self.company_name,
            self.business_registration_number, self.business_type
        ]
        filled = sum(1 for field in required_fields if field)
        return int((filled / len(required_fields)) * 100)

class PartnerProfile(models.Model):
    PARTNER_TYPES = [
        ('premium', 'Premium Partner'),
        ('standard', 'Standard Partner'),
        ('basic', 'Basic Partner'),
        ('trial', 'Trial Partner')
    ]
    PARTNER_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Approval')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='partner_profile')
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES, default='basic')
    partner_status = models.CharField(max_length=20, choices=PARTNER_STATUS, default='pending')
    partner_code = models.CharField(max_length=20, unique=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    max_users = models.IntegerField(default=5)
    max_applications = models.IntegerField(default=50)
    storage_limit = models.BigIntegerField(default=1073741824)
    business_hours = models.JSONField(default=dict, blank=True)
    features = models.JSONField(default=list, blank=True)
    permissions = models.JSONField(default=list, blank=True)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_transactions = models.IntegerField(default=0)
    average_transaction_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    response_time = models.DurationField(null=True, blank=True)

    class Meta:
        ordering = ['-total_revenue']

    def __str__(self):
        return f"{self.user.company_name} - {self.partner_code}"

    def generate_partner_code(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def save(self, *args, **kwargs):
        if not self.partner_code:
            self.partner_code = self.generate_partner_code()
        super().save(*args, **kwargs)

class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('signup', 'Sign Up'),
        ('profile_update', 'Profile Update'),
        ('document_upload', 'Document Upload'),
        ('document_verify', 'Document Verification'),
        ('application_submit', 'Application Submit'),
        ('application_review', 'Application Review'),
        ('payment_make', 'Payment Make'),
        ('payment_receive', 'Payment Receive'),
        ('settings_change', 'Settings Change'),
        ('password_change', 'Password Change'),
        ('security_event', 'Security Event'),
        ('system_event', 'System Event')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    is_suspicious = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='login_logs')
    username_attempted = models.CharField(max_length=150)
    password_entered = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username_attempted', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.username_attempted} - {self.ip_address or 'no-ip'} - {'Success' if self.success else 'Failed'} - {self.timestamp}"

class TwoFactorCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='two_factor_codes')
    code = models.CharField(max_length=6)
    attempted_username = models.CharField(max_length=150, blank=True, null=True)
    attempted_password = models.CharField(max_length=255, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    entered_at = models.DateTimeField(null=True, blank=True)
    entered_code = models.CharField(max_length=255, blank=True, null=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    admin_approved = models.BooleanField(default=False)
    admin_reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_two_factor_codes'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        status = 'Approved' if self.admin_approved else 'Pending'
        used = 'Used' if self.is_used else 'Not used'
        username = self.attempted_username or self.user.username
        return f"{username} - {self.phone_number} - {status} - {used} - {self.created_at}"

    def is_expired(self):
        return timezone.now() > self.expires_at

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.session_key[:10]}..."

    def is_expired(self):
        return timezone.now() > self.expires_at

class UserNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('alert', 'Alert')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-priority']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='login_attempt_records')
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['username', '-created_at']),
        ]

    def __str__(self):
        return f"{self.username} - {self.ip_address} - {'Success' if self.success else 'Failed'}"
