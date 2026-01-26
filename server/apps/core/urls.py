from django.urls import path
from .views import sync_views

app_name = 'core'

urlpatterns = [
    path('', sync_views.index, name='index'),
]