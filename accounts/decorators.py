from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def account_active_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_status != 'active':
            return redirect('accounts:login')
        return function(request, *args, **kwargs)
    return wrap

def user_verified_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_verified():
            return redirect('accounts:profile')
        return function(request, *args, **kwargs)
    return wrap
