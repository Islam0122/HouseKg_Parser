from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ── Main menu ──────────────────────────────────────────────────────────────

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Квартиры"),     KeyboardButton(text="🔥 Выгодные")],
            [KeyboardButton(text="📊 Статистика"),   KeyboardButton(text="📈 Рынок")],
            [KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )


# ── Flat list navigation ───────────────────────────────────────────────────

def flats_nav(page: int, total_pages: int, filters: dict = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if page > 1:
        builder.button(text="◀️ Назад", callback_data=f"flats:{page - 1}")
    builder.button(text=f"{page} / {total_pages}", callback_data="noop")
    if page < total_pages:
        builder.button(text="Вперёд ▶️", callback_data=f"flats:{page + 1}")

    builder.button(text="🔍 Фильтры", callback_data="filters_menu")
    builder.adjust(3, 1)
    return builder.as_markup()


# ── Flat detail ────────────────────────────────────────────────────────────

def flat_detail_kb(flat_id: int, link: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Открыть объявление", url=link)
    builder.button(text="⬅️ К списку", callback_data="flats:1")
    builder.adjust(1)
    return builder.as_markup()


# ── Filters menu ───────────────────────────────────────────────────────────

def filters_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="1 комн",  callback_data="filter:rooms:1")
    builder.button(text="2 комн",  callback_data="filter:rooms:2")
    builder.button(text="3 комн",  callback_data="filter:rooms:3")
    builder.button(text="4+ комн", callback_data="filter:rooms:4")
    builder.button(text="❌ Сбросить фильтры", callback_data="filter:reset")
    builder.button(text="⬅️ Назад", callback_data="flats:1")
    builder.adjust(4, 1, 1)
    return builder.as_markup()


# ── Market stats rooms selector ────────────────────────────────────────────

def market_rooms_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for r in (1, 2, 3, 4):
        builder.button(text=f"{r} комн", callback_data=f"market:{r}")
    builder.button(text="Все", callback_data="market:all")
    builder.adjust(4, 1)
    return builder.as_markup()