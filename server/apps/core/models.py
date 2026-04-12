from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    """사용자당 1개의 CS 상담 채팅방."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_room",
    )
    STATUS_CHOICES = [
        ("open", "open"),
        ("resolved", "resolved"),
        ("closed", "closed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_message_at"]

    def __str__(self):
        return f"ChatRoom({self.user})"


class ChatMessage(models.Model):
    """채팅 메시지."""

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_admin = models.BooleanField(default=False)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        role = "관리자" if self.is_admin else "사용자"
        return f"[{role}] {self.content[:30]}"
