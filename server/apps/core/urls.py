from django.urls import path

from .views import admin_views, async_views

app_name = "core"

urlpatterns = [
    # 홈
    path("", async_views.index, name="index"),
    # 사용자 CS 채팅
    path("cs/", async_views.cs_chat, name="cs_chat"),
    path("cs/send/", async_views.cs_chat_send, name="cs_chat_send"),
    path("cs/stream/", async_views.cs_chat_stream, name="cs_chat_stream"),
    # 관리자 CS 채팅
    path("cs/admin/", admin_views.cs_admin_list, name="cs_admin_list"),
    path("cs/admin/<int:room_id>/", admin_views.cs_admin_room, name="cs_admin_room"),
    path(
        "cs/admin/<int:room_id>/send/",
        admin_views.cs_admin_send,
        name="cs_admin_send",
    ),
    path(
        "cs/admin/<int:room_id>/stream/",
        admin_views.cs_admin_stream,
        name="cs_admin_stream",
    ),
    path(
        "cs/admin/<int:room_id>/status/",
        admin_views.cs_admin_status,
        name="cs_admin_status",
    ),
]
