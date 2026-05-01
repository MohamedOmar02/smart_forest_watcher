# authentication/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators     import login_required


def client_required(view_func):
    decorated_view_func = login_required(user_passes_test(
        lambda u: u.is_authenticated and hasattr(u, 'client'),
        login_url='client_login'
    )(view_func))
    return decorated_view_func


def supervisor_required(view_func):
    decorated_view_func = login_required(user_passes_test(
        lambda u: u.is_authenticated and hasattr(u, 'supervisor'),
        login_url='supervisor_login'
    )(view_func))
    return decorated_view_func
