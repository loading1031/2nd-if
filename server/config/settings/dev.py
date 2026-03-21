"""
Django settings for project - Development configuration.
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',
    'pattern_library',
]

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# Pattern library iframe rendering
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Pattern Library Configuration
PATTERN_LIBRARY = {
    "SECTIONS": (
        ("components", ["patterns/components"]),
        ("pages", ["patterns/pages"]),
    ),
    "TEMPLATE_SUFFIX": ".html",
    "PATTERN_BASE_TEMPLATE_NAME": "patterns/base.html",
    "BASE_TEMPLATE_NAMES": ["patterns/base_page.html"],
}
