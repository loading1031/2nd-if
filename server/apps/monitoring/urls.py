from django.urls import path

from . import views

app_name = "monitoring"

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("metrics/", views.prometheus_metrics, name="prometheus_metrics"),
]
