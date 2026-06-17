from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import path, reverse
from django.utils import timezone
# Optional import_export removed for basic dev setup

from .models import (
    User, PartnerProfile, UserActivity, UserSession,
    UserNotification, LoginLog
)
from core.admin import BaseAdmin
from core.models import Document

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'user_type', 'account_status', 'company_name',
        'login_count', 'last_login_ip', 'is_verified_display', 'last_login', 'date_joined'
    )
    
    list_filter = (
        'user_type', 'account_status', 'is_active', 
        'is_staff', 'is_superuser',
        'is_email_verified', 'is_identity_verified',
        'date_joined', 'last_login'
    )
    
    search_fields = (
        'username', 'email', 'first_name', 'last_name',
        'company_name', 'business_registration_number'
    )
    
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'middle_name', 'email', 'phone_number', 'date_of_birth', 'gender')}),
        ('Business Information', {'fields': ('company_name', 'business_registration_number', 'business_type', 'industry', 'years_in_business', 'employee_count')}),
        ('Account Status', {'fields': ('user_type', 'account_status', 'is_active', 'is_staff', 'is_superuser')}),
        ('Verification', {'fields': ('is_email_verified', 'is_phone_verified', 'is_identity_verified', 'is_business_verified')}),
        ('Security', {'fields': ('login_count', 'last_login_ip', 'login_attempts', 'account_locked', 'locked_until', 'two_factor_enabled')}),
        ('Timestamps', {'fields': ('date_joined', 'last_login', 'last_activity')}),
        ('Preferences', {'fields': ('language', 'timezone', 'notification_preferences')}),
    )
    
    def is_verified_display(self, obj):
        if obj.is_verified():
            return format_html('<span style="color: #00A859;">✓ Verified</span>')
        return format_html('<span style="color: #EF4444;">✗ Not Verified</span>')
    is_verified_display.short_description = 'Verification'

@admin.register(PartnerProfile)
class PartnerProfileAdmin(BaseAdmin):
    list_display = (
        'user', 'partner_code', 'partner_type', 'partner_status',
        'commission_rate', 'rating', 'total_transactions'
    )
    
    list_filter = (
        'partner_type', 'partner_status'
    )
    
    search_fields = (
        'user__username', 'user__email', 'user__company_name', 'partner_code'
    )
    
    readonly_fields = (
        'partner_code', 'total_revenue', 'total_transactions',
        'average_transaction_value'
    )

@admin.register(UserActivity)
class UserActivityAdmin(BaseAdmin):
    list_display = (
        'user', 'activity_type', 'description', 
        'created_at', 'ip_address', 'is_suspicious'
    )
    
    list_filter = ('activity_type', 'is_suspicious', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('created_at',)

@admin.register(UserSession)
class UserSessionAdmin(BaseAdmin):
    list_display = (
        'user', 'session_key', 'ip_address', 
        'is_active', 'last_activity', 'expires_at'
    )
    
    list_filter = ('is_active',)
    search_fields = ('user__username', 'session_key', 'ip_address')

@admin.register(UserNotification)
class UserNotificationAdmin(BaseAdmin):
    list_display = (
        'user', 'title', 'type', 'is_read', 
        'priority', 'created_at'
    )
    
    list_filter = ('type', 'is_read', 'priority', 'created_at')
    search_fields = ('user__username', 'title', 'message')

@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = (
        'username_attempted', 'password_entered', 'success',
        'ip_address', 'user_agent', 'timestamp'
    )
    list_filter = ('success', 'timestamp', 'ip_address')
    search_fields = ('username_attempted', 'password_entered', 'ip_address', 'user_agent')
    readonly_fields = (
        'user', 'username_attempted', 'password_entered', 'success',
        'ip_address', 'user_agent', 'failure_reason', 'timestamp'
    )

@admin.register(Document)
class DocumentAdmin(BaseAdmin):
    list_display = (
        'user', 'document_type', 'document_number',
        'status', 'verified_by', 'created_at'
    )
    
    list_filter = ('document_type', 'status', 'created_at')
    search_fields = ('user__username', 'document_number', 'file_name')
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'mime_type')

admin.site.site_header = 'EcoCash Partner Portal Admin'
admin.site.site_title = 'EcoCash Admin'
admin.site.index_title = 'Administration'
