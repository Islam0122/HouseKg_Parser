from .models import Flat, MarketStat, ParserSettings, FlatImage, ParserLog


def save_flats(flats: list, source: str) -> int:
    new_count = 0
    for data in flats:
        images = data.pop("images", [])
        flat, created = Flat.objects.get_or_create(
            link=data["link"], defaults=data
        )
        if created:
            for url in images:
                FlatImage.objects.create(flat=flat, image_url=url)
            new_count += 1

    ParserLog.objects.create(
        source=source,
        message=f"Сохранено {new_count} новых квартир",
        is_error=False
    )
    return new_count


def get_profitable_flats(already_sent_ids: set) -> list:
    result = []

    for setting in ParserSettings.objects.filter(is_active=True):
        qs = Flat.objects.filter(price_per_m2__isnull=False).exclude(
            id__in=already_sent_ids
        )

        if setting.min_rooms:
            qs = qs.filter(rooms__gte=setting.min_rooms)
        if setting.max_rooms:
            qs = qs.filter(rooms__lte=setting.max_rooms)
        if setting.district:
            qs = qs.filter(district__icontains=setting.district)

        for flat in qs:
            stat = MarketStat.objects.filter(rooms=flat.rooms).first()
            if not stat:
                continue

            threshold = stat.median_price_per_m2 * (
                1 - setting.discount_percent / 100
            )
            if flat.price_per_m2 <= threshold:
                result.append(flat)

    return result