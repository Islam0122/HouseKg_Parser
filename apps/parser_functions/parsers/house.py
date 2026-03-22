import requests
from bs4 import BeautifulSoup
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def parse_price(text):
    try:
        return int(text.replace("$", "").replace(" ", ""))
    except:
        return None


def parse_details(title):
    rooms = None
    area = None
    floor = None
    total_floors = None

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


def parse_house(max_pages=5):
    all_flats = []

    for page in range(1, max_pages + 1):
        url = f"https://www.house.kg/kupit-kvartiru?page={page}"
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        page_flats = []

        for item in soup.select(".listing"):  # или актуальный селектор
            try:
                title_tag = item.select_one(".title a")
                title = title_tag.text.strip()
                link = "https://house.kg" + title_tag["href"]

                price_text = item.select_one(".price")
                price = parse_price(price_text.text.strip()) if price_text else None

                address_tag = item.select_one(".address")
                address = address_tag.text.strip() if address_tag else None

                rooms, area, floor, total_floors = parse_details(title)

                price_per_m2 = round(price / area, 2) if price and area else None

                images = []
                for img in item.select("img"):
                    src = img.get("data-src") or img.get("src")
                    if src:
                        images.append(src)

                page_flats.append({
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
                print("Ошибка:", e)
                continue

        if not page_flats:
            break  # если на странице нет объявлений — значит мы дошли до конца

        all_flats.extend(page_flats)

    return all_flats

if __name__ == "__main__":
    data = parse_house()

    # вывод
    print(json.dumps(data, indent=100, ensure_ascii=False))

    # сохранить в файл
    with open("flats.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=100, ensure_ascii=False)