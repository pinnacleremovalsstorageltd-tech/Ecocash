from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('two-factor/', views.TwoFactorVerifyView.as_view(), name='two_factor'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('settings/', views.settings_view, name='settings'),
    path('password-change/', views.password_change, name='password_change'),

    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/<uuid:notification_id>/read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/read-all/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),
    path('api/activity/', views.api_user_activity, name='api_user_activity'),
    path('health/', views.health_check, name='health_check'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    # Educational demo - local only
    path('password-demo/', views.password_demo, name='password_demo'),
]
