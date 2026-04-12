from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone

from .models import ChatMessage, ChatRoom


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("user_nickname", "last_message_preview", "unread_badge", "status", "time_ago")
    list_filter = ("status",)
    search_fields = ("user__email", "user__nickname")
    ordering = ("-last_message_at",)
    list_per_page = 20

    def has_add_permission(self, request):
        return False

    def user_nickname(self, obj):
        return obj.user.nickname or obj.user.email

    user_nickname.short_description = "사용자"

    def last_message_preview(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if msg:
            prefix = "[관리자] " if msg.is_admin else ""
            return f"{prefix}{msg.content[:40]}"
        return "-"

    last_message_preview.short_description = "마지막 메시지"

    def unread_badge(self, obj):
        from django.utils.html import format_html

        count = obj.messages.filter(is_admin=False, is_read=False).count()
        if count:
            return format_html(
                '<span style="background:#dc3545;color:white;padding:2px 8px;border-radius:10px;font-size:12px;">{}</span>',
                count,
            )
        return ""

    unread_badge.short_description = "미읽음"

    def time_ago(self, obj):
        if not obj.last_message_at:
            return "-"
        delta = timezone.now() - obj.last_message_at
        if delta.days > 0:
            return f"{delta.days}일 전"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours}시간 전"
        minutes = delta.seconds // 60
        return f"{minutes}분 전"

    time_ago.short_description = "최근"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:room_id>/chat/",
                self.admin_site.admin_view(self.chat_view),
                name="core_chatroom_chat",
            ),
            path(
                "<int:room_id>/send/",
                self.admin_site.admin_view(self.send_view),
                name="core_chatroom_send",
            ),
            path(
                "<int:room_id>/status/",
                self.admin_site.admin_view(self.status_view),
                name="core_chatroom_status",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """기본 목록 뷰 — 클릭하면 채팅으로 이동하도록 안내."""
        extra_context = extra_context or {}
        extra_context["title"] = "CS 상담 관리"
        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """상세 뷰 클릭 시 채팅 뷰로 리다이렉트."""
        return HttpResponseRedirect(reverse("admin:core_chatroom_chat", args=[object_id]))

    def chat_view(self, request, room_id):
        """채팅 화면."""
        room = ChatRoom.objects.select_related("user").get(pk=room_id)
        messages = room.messages.select_related("sender").order_by("created_at")

        # 사용자 메시지 읽음 처리
        room.messages.filter(is_admin=False, is_read=False).update(is_read=True)

        context = {
            **self.admin_site.each_context(request),
            "room": room,
            "messages": messages,
            "title": f"{room.user.nickname or room.user.email} 채팅",
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/core/chatroom/chat.html", context)

    def send_view(self, request, room_id):
        """관리자 답변 전송."""
        if request.method != "POST":
            return HttpResponse(status=405)

        room = ChatRoom.objects.get(pk=room_id)
        content = request.POST.get("content", "").strip()
        if content:
            ChatMessage.objects.create(
                room=room,
                sender=request.user,
                is_admin=True,
                content=content,
            )
            room.last_message_at = timezone.now()
            room.save(update_fields=["last_message_at"])

        return HttpResponseRedirect(reverse("admin:core_chatroom_chat", args=[room_id]))

    def status_view(self, request, room_id):
        """상태 변경."""
        if request.method != "POST":
            return HttpResponse(status=405)

        room = ChatRoom.objects.get(pk=room_id)
        new_status = request.POST.get("status", "")
        if new_status in ("open", "resolved", "closed"):
            room.status = new_status
            room.save(update_fields=["status"])

        return HttpResponseRedirect(reverse("admin:core_chatroom_chat", args=[room_id]))
