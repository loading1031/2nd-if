"""
Synchronous views for core app.
"""
from django.shortcuts import render


def index(request):
    """Home page view."""
    return render(request, 'core/pages/index.html')
