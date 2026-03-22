from django.urls import path

from .views import async_views

app_name = "core"

urlpatterns = [
    path("", async_views.index, name="index"),
]
