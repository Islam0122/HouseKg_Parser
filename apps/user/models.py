telegram_id = models.BigIntegerField(
    unique=True,
    db_index=True,
    verbose_name="Telegram ID"
)

username = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    verbose_name="Username / Ник"
)
fullname = models.CharField(
    max_length=100,
    blank=True,
    null=True,
)

created_at = models.DateTimeField(
    default=timezone.now,
    verbose_name="Created at / Создан"
)

updated_at = models.DateTimeField(
    auto_now=True,
    verbose_name="Updated at / Обновлён"
)


class Meta:
    ordering = ["-created_at"]
    verbose_name = "Пользователь"
    verbose_name_plural = "Пользователи"


def __str__(self):
    return f"{self.telegram_id} | {self.role}"
