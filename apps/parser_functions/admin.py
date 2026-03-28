from django.contrib import admin
from django.utils.html import format_html
from .models import ParserSettings, Flat, FlatImage, MarketStat, ParserLog


class FlatImageInline(admin.TabularInline):
    model = FlatImage
    extra = 0
    readonly_fields = ("preview", "created_at")
    fields = ("preview", "image_url", "created_at")

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width:120px;height:80px;object-fit:cover;'
                'border-radius:8px;border:1px solid #e5e7eb;" />',
                obj.image_url,
            )
        return "—"


@admin.register(ParserSettings)
class ParserSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "colored_status",
        "discount_percent",
        "rooms_range",
        "district",
        "created_at",
    )
    list_filter = ("is_active", "district")
    search_fields = ("name", "district")
    ordering = ("-created_at",)
    list_editable = ("discount_percent",)

    fieldsets = (
        ("Основное", {
            "fields": ("name", "is_active"),
        }),
        ("Фильтры поиска", {
            "fields": ("min_rooms", "max_rooms", "district"),
            "description": "Настройте параметры фильтрации объявлений.",
        }),
        ("Условия выгоды", {
            "fields": ("discount_percent",),
            "description": "Объявление считается выгодным, если цена ниже рынка на указанный процент.",
        }),
    )

    @admin.display(description="Статус")
    def colored_status(self, obj):
        # ✅ Исправлено: Django 6 требует аргументы в format_html
        if obj.is_active:
            label = "✓ Активно"
            bg, color = "#d1fae5", "#065f46"
        else:
            label = "✗ Неактивно"
            bg, color = "#fee2e2", "#991b1b"
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            bg, color, label,
        )

    @admin.display(description="Комнаты")
    def rooms_range(self, obj):
        mn = obj.min_rooms or "—"
        mx = obj.max_rooms or "—"
        return f"{mn} → {mx}"


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = (
        "first_photo",
        "short_title",
        "price_badge",
        "price_per_m2_display",
        "rooms",
        "area",
        "floor_display",
        "district",
        "source_badge",
        "flags",
        "open_link",
        "created_at",
    )
    list_filter = ("source", "rooms", "district", "is_urgent", "is_owner", "city")
    ordering = ("-created_at","price","area")
    readonly_fields = ("created_at", "open_link", "photos_gallery")
    list_per_page = 25
    date_hierarchy = "created_at"
    inlines = [FlatImageInline]

    fieldsets = (
        ("Объявление", {
            "fields": ("title", "source", "link", "open_link", "created_at"),
        }),
        ("Цена", {
            "fields": ("price", "price_per_m2"),
        }),
        ("Параметры квартиры", {
            "fields": ("rooms", "area", "floor", "total_floors"),
        }),
        ("Местоположение", {
            "fields": ("city", "district", "address"),
        }),
        ("Метки", {
            "fields": ("is_urgent", "is_owner"),
        }),
    )

    @admin.display(description="Фото")
    def first_photo(self, obj):
        first = obj.images.first()
        if first:
            return format_html(
                '<img src="{}" style="width:64px;height:44px;object-fit:cover;'
                'border-radius:6px;border:1px solid #e5e7eb;" />',
                first.image_url,
            )
        return format_html(
            '<div style="width:64px;height:44px;background:#f3f4f6;'
            'border-radius:6px;display:flex;align-items:center;'
            'justify-content:center;color:#9ca3af;font-size:18px;">{}</div>',
            "🏠",
        )

    @admin.display(description="Галерея фото")
    def photos_gallery(self, obj):
        images = obj.images.all()
        if not images:
            return "Фотографий нет"
        imgs_html = "".join(
            f'<a href="{img.image_url}" target="_blank">'
            f'<img src="{img.image_url}" style="'
            f'width:160px;height:110px;object-fit:cover;'
            f'border-radius:8px;border:1px solid #e5e7eb;margin:4px;" /></a>'
            for img in images
        )
        return format_html(
            '<div style="display:flex;flex-wrap:wrap;gap:4px;">{}</div>',
            imgs_html,
        )

    @admin.display(description="Заголовок")
    def short_title(self, obj):
        title = obj.title[:50] + "…" if len(obj.title) > 50 else obj.title
        return format_html('<span title="{}">{}</span>', obj.title, title)

    @admin.display(description="Цена ($)", ordering="price")
    def price_badge(self, obj):
        # ✅ Исправлено: форматируем число до передачи в format_html
        price_str = "{:,}".format(obj.price).replace(",", " ")
        return format_html('<strong style="font-size:13px;">${}</strong>', price_str)

    @admin.display(description="$/м²", ordering="price_per_m2")
    def price_per_m2_display(self, obj):
        if obj.price_per_m2 is None:
            return "—"
        # ✅ Исправлено: форматируем до передачи
        val = "{:,.0f}".format(obj.price_per_m2).replace(",", " ")
        return format_html('<span style="color:#6b7280;">{}</span>', val)

    @admin.display(description="Этаж")
    def floor_display(self, obj):
        if obj.floor is None:
            return "—"
        total = f"/{obj.total_floors}" if obj.total_floors else ""
        return f"{obj.floor}{total}"

    @admin.display(description="Источник")
    def source_badge(self, obj):
        colors = {
            "house":  ("#eff6ff", "#1d4ed8", "House.kg"),
            "lalafo": ("#faf5ff", "#7e22ce", "Lalafo.kg"),
        }
        bg, fg, label = colors.get(obj.source, ("#f3f4f6", "#374151", obj.source))
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;'
            'border-radius:10px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, label,
        )

    @admin.display(description="Метки")
    def flags(self, obj):
        parts = []
        if obj.is_urgent:
            parts.append(
                '<span style="background:#fff7ed;color:#c2410c;padding:2px 7px;'
                'border-radius:10px;font-size:11px;">🔥 Срочно</span>'
            )
        if obj.is_owner:
            parts.append(
                '<span style="background:#f0fdf4;color:#15803d;padding:2px 7px;'
                'border-radius:10px;font-size:11px;">👤 Хозяин</span>'
            )
        if parts:
            return format_html(" ".join(parts))
        return "—"

    @admin.display(description="Ссылка")
    def open_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank" style="color:#2563eb;text-decoration:none;">'
            '↗ Открыть</a>',
            obj.link,
        )


@admin.register(MarketStat)
class MarketStatAdmin(admin.ModelAdmin):
    list_display = (
        "rooms",
        "district",
        "avg_price_per_m2",
        "median_price_per_m2",
        "diff_display",
        "updated_at",
    )
    list_filter = ("rooms", "district")
    search_fields = ("district",)
    ordering = ("rooms", "district")
    readonly_fields = ("updated_at",)

    @admin.display(description="Разница ср/мед")
    def diff_display(self, obj):
        diff = obj.avg_price_per_m2 - obj.median_price_per_m2
        pct = (diff / obj.median_price_per_m2 * 100) if obj.median_price_per_m2 else 0
        color = "#dc2626" if diff > 0 else "#16a34a"
        sign = "+" if diff >= 0 else ""
        # ✅ Исправлено: форматируем строку до передачи
        text = f"{sign}{diff:.0f} ({sign}{pct:.1f}%)"
        return format_html('<span style="color:{};">{}</span>', color, text)


@admin.register(ParserLog)
class ParserLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "source_badge",
        "level_badge",
        "short_message",
    )
    list_filter = ("source", "is_error", "created_at")
    search_fields = ("message",)
    ordering = ("-created_at",)
    readonly_fields = ("source", "message", "is_error", "created_at")
    list_per_page = 50
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Источник")
    def source_badge(self, obj):
        colors = {
            "house":  ("#eff6ff", "#1d4ed8", "House.kg"),
            "lalafo": ("#faf5ff", "#7e22ce", "Lalafo.kg"),
        }
        bg, fg, label = colors.get(obj.source, ("#f3f4f6", "#374151", obj.source))
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;'
            'border-radius:10px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, label,
        )

    @admin.display(description="Уровень")
    def level_badge(self, obj):
        if obj.is_error:
            return format_html(
                '<span style="background:#fef2f2;color:#b91c1c;padding:2px 9px;'
                'border-radius:10px;font-size:11px;font-weight:700;">{}</span>',
                "⛔ Ошибка",
            )
        return format_html(
            '<span style="background:#f0fdf4;color:#166534;padding:2px 9px;'
            'border-radius:10px;font-size:11px;font-weight:600;">{}</span>',
            "✓ Инфо",
        )

    @admin.display(description="Сообщение")
    def short_message(self, obj):
        msg = obj.message[:120] + "…" if len(obj.message) > 120 else obj.message
        color = "#b91c1c" if obj.is_error else "#374151"
        return format_html(
            '<span style="color:{};font-family:monospace;font-size:12px;">{}</span>',
            color, msg,
        )