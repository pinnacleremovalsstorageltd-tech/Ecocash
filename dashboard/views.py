from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'dashboard/index.html')

@login_required
def applications(request):
    return render(request, 'dashboard/applications.html')

@login_required
def payments(request):
    return render(request, 'dashboard/payments.html')

@login_required
def reports(request):
    return render(request, 'dashboard/reports.html')
