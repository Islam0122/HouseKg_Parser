from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "username", "fullname", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("telegram_id", "username", "fullname")
    list_editable = ("is_active",)