from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('applications/', views.applications, name='applications'),
    path('payments/', views.payments, name='payments'),
    path('reports/', views.reports, name='reports'),
]
