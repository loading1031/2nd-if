"""
URL configuration for project.
"""
from django.apps import apps
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('accounts/', include('allauth.urls')),
    path('stories/', include('apps.stories.urls')),
]

# Pattern library (development only)
if apps.is_installed('pattern_library'):
    urlpatterns += [
        path('pattern-library/', include('pattern_library.urls')),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
