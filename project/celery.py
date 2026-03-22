import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Парсинг — каждый час в :00
    "parse-every-hour": {
        "task": "apps.parser_functions.tasks.run_parser",
        "schedule": crontab(minute=0),
    },
    # Уведомления — каждые 30 минут в :00 и :30
    "notify-every-30-min": {
        "task": "apps.parser_functions.tasks.notify_profitable_flats",
        "schedule": crontab(minute="*/15"),
    },
}