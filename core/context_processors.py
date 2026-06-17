def site_settings(request):
    from django.conf import settings
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'VERSION': settings.VERSION,
    }
