from django.contrib import admin
from django.utils.html import format_html
from .models import Chat, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "short_text", "meta", "created_at")
    fields = ("role", "short_text", "meta", "created_at")
    ordering = ("created_at",)
    can_delete = False
    verbose_name = "Сообщение"
    verbose_name_plural = "Сообщения"

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Текст")
    def short_text(self, obj):
        return obj.text[:100] + "…" if len(obj.text) > 100 else obj.text


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "platform_badge",
        "user",
        "external_id",
        "language",
        "message_count",
        "created_at",
    )
    list_filter = ("chat_type", "language", "created_at")
    search_fields = ("external_id", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "message_count")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    inlines = [MessageInline]
    list_per_page = 25

    fieldsets = (
        ("Основная информация", {
            "fields": ("chat_type", "user", "external_id", "language"),
            "description": "Основные параметры чата и привязка к пользователю.",
        }),
        ("Кэш сообщений", {
            "fields": ("messages_cache",),
            "classes": ("collapse",),
            "description": "JSON-кэш последних сообщений для быстрого доступа.",
        }),
        ("Служебное", {
            "fields": ("created_at", "updated_at", "message_count"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Платформа")
    def platform_badge(self, obj):
        colors = {
            "website":  ("#eff6ff", "#1d4ed8", "🌐 Website"),
            "telegram": ("#f0fdf4", "#15803d", "✈️ Telegram"),
            "whatsapp": ("#f0fdf4", "#166534", "💬 WhatsApp"),
        }
        bg, color, label = colors.get(obj.chat_type, ("#f3f4f6", "#374151", obj.chat_type))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            bg, color, label,
        )

    @admin.display(description="Сообщений")
    def message_count(self, obj):
        count = obj.messages.count()
        color = "#16a34a" if count > 0 else "#9ca3af"
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            color, count,
        )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat_link",
        "role_badge",
        "short_text",
        "has_meta",
        "created_at",
    )
    list_filter = ("role", "created_at")
    search_fields = ("text", "chat__external_id", "chat__user__username")
    readonly_fields = ("chat", "role", "text", "meta", "created_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        ("Сообщение", {
            "fields": ("chat", "role", "text"),
            "description": "Содержимое сообщения и его роль в диалоге.",
        }),
        ("Метаданные", {
            "fields": ("meta", "created_at"),
            "classes": ("collapse",),
            "description": "Дополнительные данные и временные метки.",
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Чат")
    def chat_link(self, obj):
        return format_html(
            '<a href="/admin/chat/chat/{}/change/" style="color:#2563eb;text-decoration:none;">'
            'Чат #{}</a>',
            obj.chat_id, obj.chat_id,
        )

    @admin.display(description="Роль")
    def role_badge(self, obj):
        colors = {
            "user":      ("#eff6ff", "#1d4ed8", "👤 Пользователь"),
            "assistant": ("#faf5ff", "#7e22ce", "🤖 Ассистент"),
            "system":    ("#fff7ed", "#c2410c", "⚙️ Система"),
        }
        bg, color, label = colors.get(obj.role, ("#f3f4f6", "#374151", obj.role))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            bg, color, label,
        )

    @admin.display(description="Текст")
    def short_text(self, obj):
        text = obj.text[:100] + "…" if len(obj.text) > 100 else obj.text
        return format_html(
            '<span style="font-size:13px;color:#374151;">{}</span>',
            text,
        )

    @admin.display(description="Мета", boolean=True)
    def has_meta(self, obj):
        return bool(obj.meta)