from django.urls import path

from .views import upload_views

# These should be included at /api/ prefix in config/urls.py
app_name = 'stories_api'

urlpatterns = [
    path('upload-image/', upload_views.upload_image, name='upload_image'),
]
