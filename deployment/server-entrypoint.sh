#!/bin/sh
set -e

# Используем виртуальное окружение
. .venv/bin/activate

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Создание суперпользователя, если нет
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

# Запуск Gunicorn
exec gunicorn project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --log-level info