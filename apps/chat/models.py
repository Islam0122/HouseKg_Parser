from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatPlatform(models.TextChoices):
    WEBSITE = "website", "Website"
    TELEGRAM = "telegram", "Telegram"
    WHATSAPP = "whatsapp", "WhatsApp"


class UserType(models.TextChoices):
    GUEST = "guest", "Guest"
    USER = "user", "User"
    TG_USER = "tg_user", "Telegram User"


class Chat(models.Model):
    chat_type = models.CharField(
        max_length=20,
        choices=ChatPlatform.choices,
        default=ChatPlatform.WEBSITE,
        verbose_name="Тип платформы",
        db_index=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chats",
        null=True,
        blank=True,
        verbose_name="Пользователь",
        db_index=True,
    )
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.GUEST,
        verbose_name="Тип пользователя",
    )
    language = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name="Язык",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Чат #{self.id} ({self.chat_type}) user={self.user_id}"


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages_set",
        verbose_name="Чат",
        db_index=True,
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        verbose_name="Роль",
    )
    text = models.TextField(verbose_name="Текст")

    meta = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Мета",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["chat", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.role}] {self.text[:60]}"