import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "parse-every-30-min": {
        "task": "apps.parser_functions.tasks.run_parser",
        "schedule": crontab(minute="*/1"),
    },
}