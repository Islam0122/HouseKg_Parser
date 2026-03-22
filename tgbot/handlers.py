import math
import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import api
from formatters import (
    fmt_flat_card,
    fmt_flat_detail,
    fmt_profitable_card,
    fmt_stats,
    fmt_market_stats,
)
from keyboards import (
    main_menu,
    flats_nav,
    flat_detail_kb,
    filters_menu_kb,
    market_rooms_kb,
)

logger = logging.getLogger(__name__)
router = Router()

PAGE_SIZE = 20  # должен совпадать с PAGE_SIZE в Django


# ── /start ─────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await api.register_user(
        telegram_id=user.id,
        username=user.username,
        fullname=user.full_name,
    )
    await message.answer(
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        "Я помогу найти выгодные квартиры в Бишкеке 🏠\n"
        "Выбери раздел в меню 👇",
        reply_markup=main_menu(),
    )


# ── /help ──────────────────────────────────────────────────────────────────

@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Как пользоваться ботом</b>\n\n"
        "🏠 <b>Квартиры</b> — все объявления с пагинацией и фильтрами\n"
        "🔥 <b>Выгодные</b> — квартиры дешевле рынка по настройкам\n"
        "📊 <b>Статистика</b> — общие цифры по базе\n"
        "📈 <b>Рынок</b> — средние цены по районам и комнатам\n\n"
        "В списке квартир нажми на заголовок, чтобы увидеть детали.",
        reply_markup=main_menu(),
    )


# ── Квартиры (список) ──────────────────────────────────────────────────────

async def _send_flats_page(message_or_query, page: int, filters: dict = None):
    """Универсальная функция отправки страницы квартир."""
    filters = filters or {}
    data = await api.get_flats(page=page, **filters)

    if not data or not data.get("results"):
        text = "😕 Квартиры не найдены."
        if isinstance(message_or_query, Message):
            await message_or_query.answer(text)
        else:
            await message_or_query.message.edit_text(text)
        return

    total   = data["count"]
    results = data["results"]
    total_pages = max(1, math.ceil(total / PAGE_SIZE))

    lines = [f"🏠 <b>Квартиры</b>  (стр. {page}/{total_pages}, всего {total})\n"]
    for i, flat in enumerate(results, start=(page - 1) * PAGE_SIZE + 1):
        lines.append(fmt_flat_card(flat, index=i))
        lines.append("─" * 28)

    text = "\n".join(lines)
    kb   = flats_nav(page, total_pages)

    if isinstance(message_or_query, Message):
        await message_or_query.answer(text, reply_markup=kb, disable_web_page_preview=True)
    else:
        await message_or_query.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)


@router.message(F.text == "🏠 Квартиры")
async def btn_flats(message: Message):
    await _send_flats_page(message, page=1)


@router.callback_query(F.data.startswith("flats:"))
async def cb_flats_page(query: CallbackQuery):
    page = int(query.data.split(":")[1])
    await _send_flats_page(query, page=page)
    await query.answer()


# ── Детали квартиры ────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("flat:"))
async def cb_flat_detail(query: CallbackQuery):
    flat_id = int(query.data.split(":")[1])
    flat = await api.get_flat(flat_id)

    if not flat:
        await query.answer("Квартира не найдена.", show_alert=True)
        return

    images = flat.get("images", [])
    text   = fmt_flat_detail(flat)
    kb     = flat_detail_kb(flat_id, flat["link"])

    if images:
        await query.message.answer_photo(
            photo=images[0]["image_url"],
            caption=text,
            reply_markup=kb,
        )
    else:
        await query.message.answer(text, reply_markup=kb, disable_web_page_preview=True)

    await query.answer()


# ── Выгодные квартиры ──────────────────────────────────────────────────────

@router.message(F.text == "🔥 Выгодные")
async def btn_profitable(message: Message):
    await message.answer("⏳ Ищу выгодные квартиры...")
    data = await api.get_profitable_flats()

    if not data or not data.get("results"):
        await message.answer(
            "😕 Выгодных квартир пока нет.\n"
            "Парсер обновляет базу каждый час."
        )
        return

    flats = data["results"]
    lines = [f"🔥 <b>Выгодные квартиры</b>  ({data['count']} шт.)\n"]
    for i, flat in enumerate(flats[:15], start=1):
        lines.append(fmt_profitable_card(flat, index=i))
        lines.append("─" * 28)

    await message.answer(
        "\n".join(lines),
        disable_web_page_preview=True,
    )


# ── Статистика ─────────────────────────────────────────────────────────────

@router.message(F.text == "📊 Статистика")
async def btn_stats(message: Message):
    data = await api.get_stats()
    if not data:
        await message.answer("❌ Не удалось получить статистику.")
        return
    await message.answer(fmt_stats(data))


# ── Рынок ──────────────────────────────────────────────────────────────────

@router.message(F.text == "📈 Рынок")
async def btn_market(message: Message):
    await message.answer(
        "📈 Выбери количество комнат:",
        reply_markup=market_rooms_kb(),
    )


@router.callback_query(F.data.startswith("market:"))
async def cb_market(query: CallbackQuery):
    rooms_raw = query.data.split(":")[1]
    rooms = None if rooms_raw == "all" else int(rooms_raw)

    data = await api.get_market_stats(rooms=rooms)
    if not data:
        await query.answer("❌ Нет данных.", show_alert=True)
        return

    rows = data if isinstance(data, list) else data.get("results", [])
    await query.message.edit_text(fmt_market_stats(rows))
    await query.answer()


# ── Фильтры ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "filters_menu")
async def cb_filters_menu(query: CallbackQuery):
    await query.message.edit_text(
        "🔍 <b>Фильтры</b>\nВыбери количество комнат:",
        reply_markup=filters_menu_kb(),
    )
    await query.answer()


@router.callback_query(F.data.startswith("filter:rooms:"))
async def cb_filter_rooms(query: CallbackQuery):
    rooms = int(query.data.split(":")[2])
    await _send_flats_page(query, page=1, filters={"min_rooms": rooms, "max_rooms": rooms})
    await query.answer(f"Фильтр: {rooms} комн.")


@router.callback_query(F.data == "filter:reset")
async def cb_filter_reset(query: CallbackQuery):
    await _send_flats_page(query, page=1)
    await query.answer("Фильтры сброшены")


# ── Noop ───────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "noop")
async def cb_noop(query: CallbackQuery):
    await query.answer()