from django.db import models
from django.utils import timezone


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True,
        db_index=True,
        verbose_name="Telegram ID"
    )
    username = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Username"
    )
    fullname = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name="Имя"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.telegram_id} | {self.username or self.fullname}"