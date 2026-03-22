from typing import Optional


def fmt_flat_card(flat: dict, index: int = None) -> str:
    """Короткая карточка для списка."""
    num = f"{index}. " if index else ""
    price = f"${flat['price']:,}".replace(",", " ")
    ppm2  = f" | <b>{flat['price_per_m2']:.0f} $/м²</b>" if flat.get("price_per_m2") else ""
    rooms = f"{flat['rooms']}-комн. " if flat.get("rooms") else ""
    area  = f"{flat['area']} м²" if flat.get("area") else ""
    floor = f"  🏢 {flat['floor_info']} эт." if flat.get("floor_info") else ""
    dist  = f"  📍 {flat['district']}" if flat.get("district") else ""
    flags = _flags(flat)

    return (
        f"{num}<b>{rooms}{area}</b>{floor}{dist}\n"
        f"💰 <b>{price}</b>{ppm2}{flags}\n"
        f"<a href='{flat['link']}'>↗ Открыть</a>"
    )


def fmt_flat_detail(flat: dict) -> str:
    """Полная карточка для детального просмотра."""
    price = f"${flat['price']:,}".replace(",", " ")
    ppm2  = f"{flat['price_per_m2']:.0f} $/м²" if flat.get("price_per_m2") else "—"
    rooms = f"{flat['rooms']}" if flat.get("rooms") else "—"
    area  = f"{flat['area']} м²" if flat.get("area") else "—"
    floor = flat.get("floor_info") or "—"
    dist  = flat.get("district") or "—"
    addr  = flat.get("address") or "—"
    src   = "House.kg" if flat.get("source") == "house" else "Lalafo.kg"
    flags = _flags(flat)

    return (
        f"🏠 <b>{flat['title']}</b>\n\n"
        f"💰 <b>{price}</b>  |  {ppm2}\n"
        f"🛏 Комнат: {rooms}   📐 Площадь: {area}\n"
        f"🏢 Этаж: {floor}   📍 Район: {dist}\n"
        f"🗺 Адрес: {addr}\n"
        f"📌 Источник: {src}{flags}"
    )


def fmt_profitable_card(flat: dict, index: int = None) -> str:
    """Карточка выгодной квартиры со скидкой от рынка."""
    base = fmt_flat_card(flat, index)
    discount = flat.get("discount_from_market")
    median   = flat.get("market_median")
    extra = ""
    if discount is not None:
        extra += f"\n🔻 Ниже рынка на <b>{discount:.1f}%</b>"
    if median is not None:
        extra += f"  (медиана: {median:.0f} $/м²)"
    return base + extra


def fmt_stats(data: dict) -> str:
    by_source = "\n".join(
        f"  • {s['source']}: {s['count']} шт." for s in data.get("by_source", [])
    )
    return (
        f"📊 <b>Сводная статистика</b>\n\n"
        f"🏠 Всего квартир: <b>{data['total_flats']}</b>\n"
        f"💰 Средняя цена: <b>${data['avg_price']:,.0f}</b>\n"
        f"📐 Средняя цена/м²: <b>{data['avg_price_per_m2']:.0f} $/м²</b>\n"
        f"⬇️ Мин. цена: ${data['min_price']:,}\n"
        f"⬆️ Макс. цена: ${data['max_price']:,}\n\n"
        f"По источникам:\n{by_source}"
    )


def fmt_market_stats(rows: list) -> str:
    if not rows:
        return "Нет данных по рынку."
    lines = ["📈 <b>Статистика рынка</b>\n"]
    current_rooms = None
    for row in rows:
        if row["rooms"] != current_rooms:
            current_rooms = row["rooms"]
            lines.append(f"\n<b>{current_rooms}-комнатные</b>")
        lines.append(
            f"  📍 {row['district']}: "
            f"ср. {row['avg_price_per_m2']:.0f} | "
            f"мед. {row['median_price_per_m2']:.0f} $/м²"
        )
    return "\n".join(lines)


def _flags(flat: dict) -> str:
    parts = []
    if flat.get("is_urgent"):
        parts.append("🔥 Срочно")
    if flat.get("is_owner"):
        parts.append("👤 Хозяин")
    return ("  " + "  ".join(parts)) if parts else ""