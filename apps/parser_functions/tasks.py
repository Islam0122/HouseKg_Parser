import logging
from celery import shared_task
from django.core.cache import cache

from .parsers.house import parse_house
from .services import save_flats, get_profitable_flats

logger = logging.getLogger(__name__)

SENT_FLATS_CACHE_KEY = "sent_flat_ids"


@shared_task
def run_parser():
    for source, parser in [("house", parse_house)]:
        try:
            flats = parser()
            count = save_flats(flats, source)
            logger.info(f"[{source}] Новых квартир: {count}")
        except Exception as e:
            logger.error(f"[{source}] Ошибка парсинга: {e}")

    notify_profitable_flats.delay()


@shared_task
def notify_profitable_flats():
    sent_ids = set(cache.get(SENT_FLATS_CACHE_KEY) or [])
    profitable = get_profitable_flats(already_sent_ids=sent_ids)

    if not profitable:
        logger.info("Выгодных квартир не найдено")
        return

    for flat in profitable:
        send_flat_notification.delay(flat.id)
        sent_ids.add(flat.id)

    cache.set(SENT_FLATS_CACHE_KEY, list(sent_ids), timeout=60 * 60 * 24 * 7)
    logger.info(f"Отправляем уведомлений: {len(profitable)}")


@shared_task
def send_flat_notification(flat_id: int):
    import requests as req
    from django.conf import settings
    from .models import Flat
    from apps.user.models import TelegramUser

    try:
        flat = Flat.objects.prefetch_related("images").get(id=flat_id)
    except Flat.DoesNotExist:
        return

    floor_info = f"{flat.floor}/{flat.total_floors}" if flat.floor else "—"
    text = (
        f"🏠 <b>{flat.title}</b>\n"
        f"💰 <b>${flat.price:,}</b>"
        + (f" | {flat.price_per_m2:.0f} $/м²" if flat.price_per_m2 else "")
        + f"\n📐 {flat.area} м²  🏢 {floor_info} эт."
        f"\n📍 {flat.address}"
        f"\n🔗 <a href='{flat.link}'>Открыть объявление</a>"
    )

    users = TelegramUser.objects.filter(is_active=True)
    bot_token = settings.BOT_TOKEN

    for user in users:
        try:
            req.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": user.telegram_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=10,
            )
        except Exception as e:
            logger.error(f"Ошибка отправки {user.telegram_id}: {e}")