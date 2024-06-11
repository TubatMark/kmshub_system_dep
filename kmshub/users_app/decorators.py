from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import (
    get_user_model,
    authenticate,
    logout,
    login as auth_login,
)


def is_ajax(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({"error": "Invalid request method or not AJAX"})

    return _wrapped_view


def is_user_authenticated(user):
    return user.is_authenticated


def is_admin_or_secretariat(user):
    return user.is_authenticated and (
        user.user_type == "admin" or user.user_type == "secretariat"
    )


def is_general_user(user):
    return user.is_authenticated and (
        user.user_type == "general" or user.user_type == "cmi"
    )


def login_required(view_func):
    decorated_view_func = user_passes_test(
        is_user_authenticated,
        login_url=reverse_lazy("login"),  # Adjust 'login' to your actual login URL
    )(view_func)
    return decorated_view_func


def admin_secretariat_required(view_func):
    decorated_view_func = user_passes_test(
        is_admin_or_secretariat,
        login_url=reverse_lazy("login"),  # Adjust 'login' to your actual login URL
    )(view_func)
    return decorated_view_func


def general_user_required(view_func):
    decorated_view_func = user_passes_test(
        is_general_user,
        login_url=reverse_lazy("login"),  # Adjust 'login' to your actual login URL
    )(view_func)
    return decorated_view_func
