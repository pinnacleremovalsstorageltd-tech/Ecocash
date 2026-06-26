from django.db import models

# Dummy models for app registration
class Dashboard(models.Model):
    class Meta:
        app_label = 'dashboard'

# Application model moved to the applications app

# Payment model lives in the payments app
