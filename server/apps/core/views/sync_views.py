"""
Synchronous views for core app.
"""
from django.shortcuts import render


def index(request):
    """Home page view."""
    return render(request, 'core/pages/index.html')


def signup_page(request):
    """Signup page view."""
    return render(request, 'core/pages/signup.html')


def login_page(request):
    """Login page view."""
    return render(request, 'core/pages/login.html')
