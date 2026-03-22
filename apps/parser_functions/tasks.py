import asyncio
import logging
import time

from celery import shared_task
from django.conf import settings
from django.db import IntegrityError

from .parsers.house import parse_house
from .services import save_flats, get_profitable_flats

logger = logging.getLogger(__name__)

# Telegram разрешает ~30 сообщений/сек глобально
# и 1 сообщение/сек на один чат.
# Ставим задержку между сообщениями разным юзерам.
TG_SEND_DELAY = 0.05   # 50 мс = ~20 сообщений/сек — безопасно
TG_RETRY_AFTER = 30    # если 429 — подождать 30 сек

# Сколько максимум квартир отправить одному юзеру за один прогон
MAX_PER_USER = 5


# ── Парсинг ────────────────────────────────────────────────────────────────

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


# ── Уведомления ────────────────────────────────────────────────────────────

@shared_task
def notify_profitable_flats():
    """
    Для каждого активного пользователя ищем выгодные квартиры,
    которые ему ещё не отправляли, и ставим задачи на отправку.
    """
    from apps.user.models import TelegramUser
    from .models import SentFlat

    users = TelegramUser.objects.filter(is_active=True)
    if not users.exists():
        logger.info("Нет активных пользователей")
        return

    # Получаем ВСЕ выгодные квартиры (без фильтра sent_ids)
    all_profitable = get_profitable_flats(already_sent_ids=set())

    if not all_profitable:
        logger.info("Выгодных квартир не найдено")
        return

    profitable_ids = [f.id for f in all_profitable]
    profitable_map = {f.id: f for f in all_profitable}

    total_queued = 0

    for user in users:
        # Какие из выгодных уже отправлены этому юзеру
        already_sent = set(
            SentFlat.objects.filter(
                user=user, flat_id__in=profitable_ids
            ).values_list("flat_id", flat=True)
        )

        # Новые для этого юзера
        new_ids = [fid for fid in profitable_ids if fid not in already_sent]

        if not new_ids:
            continue

        # Лимит за один прогон — не заспамить
        to_send = new_ids[:MAX_PER_USER]

        for flat_id in to_send:
            send_flat_to_user.delay(flat_id=flat_id, user_id=user.id)
            total_queued += 1

    logger.info(f"Поставлено в очередь уведомлений: {total_queued}")


# ── Отправка одной квартиры одному юзеру ───────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_flat_to_user(self, flat_id: int, user_id: int):
    """
    Отправляет одну квартиру одному пользователю.
    При 429 — делает retry через TG_RETRY_AFTER секунд.
    Записывает SentFlat после успешной отправки.
    """
    import requests as req
    from .models import Flat
    from apps.user.models import TelegramUser
    from .models import SentFlat

    try:
        flat = Flat.objects.prefetch_related("images").get(id=flat_id)
        user = TelegramUser.objects.get(id=user_id)
    except (Flat.DoesNotExist, TelegramUser.DoesNotExist):
        return

    bot_token = settings.BOT_TOKEN
    floor_info = f"{flat.floor}/{flat.total_floors}" if flat.floor else "—"

    text = (
        f"🏠 <b>{flat.title}</b>\n"
        f"💰 <b>${flat.price:,}</b>"
        + (f" | {flat.price_per_m2:.0f} $/м²" if flat.price_per_m2 else "")
        + f"\n📐 {flat.area} м²  🏢 {floor_info} эт."
        f"\n📍 {flat.address}"
        f"\n🔗 <a href='{flat.link}'>Открыть объявление</a>"
    )

    # Фото если есть
    first_image = flat.images.first()

    try:
        if first_image:
            resp = req.post(
                f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                json={
                    "chat_id": user.telegram_id,
                    "photo": first_image.image_url,
                    "caption": text,
                    "parse_mode": "HTML",
                },
                timeout=10,
            )
        else:
            resp = req.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": user.telegram_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=10,
            )

        # Rate limit — Telegram говорит подождать
        if resp.status_code == 429:
            retry_after = resp.json().get("parameters", {}).get("retry_after", TG_RETRY_AFTER)
            logger.warning(f"429 от Telegram для user {user.telegram_id}, retry after {retry_after}s")
            raise self.retry(countdown=retry_after)

        if resp.status_code == 403:
            # Юзер заблокировал бота — деактивируем
            logger.warning(f"Юзер {user.telegram_id} заблокировал бота — деактивируем")
            TelegramUser.objects.filter(id=user_id).update(is_active=False)
            return

        if not resp.ok:
            logger.error(f"Telegram error {resp.status_code}: {resp.text}")
            return

    except req.RequestException as e:
        logger.error(f"Сетевая ошибка при отправке {user.telegram_id}: {e}")
        raise self.retry(exc=e)

    # Успешно — запоминаем
    try:
        SentFlat.objects.create(user=user, flat=flat)
    except IntegrityError:
        pass  # уже было создано (race condition при параллельных воркерах)

    # Пауза между отправками чтобы не словить rate limit
    time.sleep(TG_SEND_DELAY)