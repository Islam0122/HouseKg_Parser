from django.db import models


class ParserSettings(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название настройки",
        help_text="Произвольное имя настройки (например: '2-комн Магистраль')"
    )

    discount_percent = models.FloatField(
        default=20,
        verbose_name="Процент ниже рынка",
        help_text="На сколько процентов цена должна быть ниже рынка (например: 20)"
    )

    min_rooms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Минимум комнат",
        help_text="Минимальное количество комнат (например: 1)"
    )

    max_rooms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Максимум комнат",
        help_text="Максимальное количество комнат (например: 3)"
    )

    district = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Район",
        help_text="Фильтр по району (например: Магистраль)"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
        help_text="Включена ли эта настройка"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Настройка парсера"
        verbose_name_plural = "Настройки парсера"

class FlatImage(models.Model):
    flat = models.ForeignKey(
        "Flat",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Квартира"
    )

    image_url = models.URLField(
        verbose_name="URL изображения",
        help_text="Ссылка на изображение квартиры"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    def __str__(self):
        return f"Фото для {self.flat.id}"

    class Meta:
        verbose_name = "Изображение квартиры"
        verbose_name_plural = "Изображения квартир"

class Flat(models.Model):
    SOURCE_CHOICES = [
        ("house", "House.kg"),
        ("lalafo", "Lalafo.kg"),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
        help_text="Название объявления"
    )

    price = models.IntegerField(
        verbose_name="Цена ($)",
        help_text="Общая стоимость квартиры"
    )

    price_per_m2 = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Цена за м²",
        help_text="Цена за квадратный метр"
    )

    rooms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Комнаты",
        help_text="Количество комнат"
    )

    area = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Площадь (м²)",
        help_text="Общая площадь квартиры"
    )

    floor = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Этаж"
    )

    total_floors = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Этажей всего"
    )

    city = models.CharField(
        max_length=100,
        default="Бишкек",
        verbose_name="Город"
    )

    district = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Район"
    )

    address = models.TextField(
        verbose_name="Адрес",
        help_text="Полный адрес объявления"
    )

    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        verbose_name="Источник"
    )

    link = models.URLField(
        unique=True,
        verbose_name="Ссылка",
        help_text="Ссылка на объявление"
    )

    is_urgent = models.BooleanField(
        default=False,
        verbose_name="Срочно"
    )

    is_owner = models.BooleanField(
        default=False,
        verbose_name="Собственник"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    def __str__(self):
        return f"{self.title} - {self.price}$"

    class Meta:
        verbose_name = "Квартира"
        verbose_name_plural = "Квартиры"
        ordering = ["-created_at"]


class MarketStat(models.Model):
    rooms = models.IntegerField(
        verbose_name="Комнаты"
    )

    district = models.CharField(
        max_length=100,
        verbose_name="Район"
    )

    avg_price_per_m2 = models.FloatField(
        verbose_name="Средняя цена за м²"
    )

    median_price_per_m2 = models.FloatField(
        verbose_name="Медианная цена за м²",
        help_text="Более точный показатель рынка"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено"
    )

    def __str__(self):
        return f"{self.rooms} комн - {self.district}"

    class Meta:
        verbose_name = "Статистика рынка"
        verbose_name_plural = "Статистика рынка"
        unique_together = ("rooms", "district")


class ParserLog(models.Model):
    SOURCE_CHOICES = [
        ("house", "House.kg"),
        ("lalafo", "Lalafo.kg"),
    ]

    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        verbose_name="Источник"
    )

    message = models.TextField(
        verbose_name="Сообщение",
        help_text="Текст ошибки или события"
    )

    is_error = models.BooleanField(
        default=False,
        verbose_name="Ошибка"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата"
    )

    class Meta:
        verbose_name = "Лог парсера"
        verbose_name_plural = "Логи парсера"
        ordering = ["-created_at"]

