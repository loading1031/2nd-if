from django.urls import path

from .views import async_views

app_name = "core"

urlpatterns = [
    path("", async_views.index, name="index"),
    path("cs/", async_views.cs_chat, name="cs_chat"),
    path("cs/chat/", async_views.cs_chat_send, name="cs_chat_send"),
]
