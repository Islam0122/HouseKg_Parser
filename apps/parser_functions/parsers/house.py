import requests
from bs4 import BeautifulSoup
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_URL = "https://www.house.kg/kupit-kvartiru"


def parse_price(text):
    try:
        return int(text.replace("$", "").replace(" ", ""))
    except:
        return None


def parse_details(title):
    rooms = area = floor = total_floors = None

    rooms_match = re.search(r"(\d+)-комн", title)
    area_match = re.search(r"(\d+\.?\d*)\s*м2", title)
    floor_match = re.search(r"(\d+)\s*этаж\s*из\s*(\d+)", title)

    if rooms_match:
        rooms = int(rooms_match.group(1))
    if area_match:
        area = float(area_match.group(1))
    if floor_match:
        floor = int(floor_match.group(1))
        total_floors = int(floor_match.group(2))

    return rooms, area, floor, total_floors


def parse_page(page: int) -> list:
    """Парсит одну страницу, возвращает список квартир."""
    url = f"{BASE_URL}?page={page}"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    items = soup.select(".listing")
    if not items:
        return []  # страница пустая — стоп

    flats = []
    for item in items:
        try:
            title_tag = item.select_one(".title a")
            title = title_tag.text.strip()
            link = "https://house.kg" + title_tag["href"]

            price_text = item.select(".price")[0].text.strip()
            price = parse_price(price_text)
            if not price:
                continue

            address = item.select_one(".address").text.strip()
            rooms, area, floor, total_floors = parse_details(title)

            price_per_m2 = round(price / area, 2) if price and area else None

            images = [
                img.get("data-src")
                for img in item.select("img")
                if img.get("data-src")
            ]

            flats.append({
                "title": title,
                "price": price,
                "price_per_m2": price_per_m2,
                "rooms": rooms,
                "area": area,
                "floor": floor,
                "total_floors": total_floors,
                "address": address,
                "city": "Бишкек",
                "district": None,
                "source": "house",
                "link": link,
                "images": images,
            })

        except Exception as e:
            print(f"Ошибка на странице {page}: {e}")
            continue

    return flats


def parse_house(max_pages: int = 20) -> list:
    """
    Парсит все страницы до упора.
    max_pages — защита от бесконечного цикла.
    """
    all_flats = []

    for page in range(1, max_pages + 1):
        print(f"Парсим страницу {page}...")
        flats = parse_page(page)

        if not flats:
            print(f"Страница {page} пустая — завершаем.")
            break

        all_flats.extend(flats)
        print(f"  Найдено: {len(flats)} квартир (всего: {len(all_flats)})")

    return all_flats