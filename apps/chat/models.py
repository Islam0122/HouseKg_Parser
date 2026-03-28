from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Chat(models.Model):
    class Platform(models.TextChoices):
        WEBSITE  = "website",  "Website"
        TELEGRAM = "telegram", "Telegram"
        WHATSAPP = "whatsapp", "WhatsApp"

    chat_type = models.CharField(
        max_length=20,
        choices=Platform.choices,
        default=Platform.WEBSITE,
        db_index=True,
        verbose_name="Платформа",
        help_text="Источник, с которого поступил чат (сайт, Telegram, WhatsApp).",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chats",
        db_index=True,
        verbose_name="Пользователь",
        help_text="Зарегистрированный пользователь, которому принадлежит чат. Может быть пустым для гостей.",
    )
    external_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Внешний ID",
        help_text="Идентификатор чата во внешней системе (например, telegram_id или session_id).",
    )
    language = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        verbose_name="Язык",
        help_text="Язык общения в чате в формате ISO 639-1 (например: ru, en, ky).",
    )
    messages_cache = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Кэш сообщений",
        help_text="JSON-список последних сообщений для быстрой передачи в LLM без запроса к БД.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Создан",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлён",
    )

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["chat_type", "created_at"]),
            models.Index(fields=["user", "chat_type"]),
        ]

    def __str__(self):
        return f"Чат #{self.pk} [{self.chat_type}] user={self.user_id}"


class Message(models.Model):
    class Role(models.TextChoices):
        USER      = "user",      "Пользователь"
        ASSISTANT = "assistant", "Ассистент"
        SYSTEM    = "system",    "Система"

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages",
        db_index=True,
        verbose_name="Чат",
        help_text="Чат, к которому относится данное сообщение.",
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        verbose_name="Роль",
        help_text="Роль отправителя: user — пользователь, assistant — ИИ, system — системный промпт.",
    )
    text = models.CharField(
        max_length=5000,
        verbose_name="Текст",
        help_text="Текст сообщения. Максимум 5000 символов.",
    )
    meta = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Метаданные",
        help_text="Произвольные метаданные: токены, модель, latency и т.д.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Создано",
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["chat", "created_at"]),
            models.Index(fields=["chat", "role"]),
        ]

    def __str__(self):
        return f"[{self.role}] чат={self.chat_id} — {self.text[:60]}"