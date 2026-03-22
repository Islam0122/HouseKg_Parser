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


def parse_house():
    url = "https://www.house.kg/kupit-kvartiru"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    flats = []

    for item in soup.select(".listing"):
        try:
            title_tag = item.select_one(".title a")
            title = title_tag.text.strip()
            link = "https://house.kg" + title_tag["href"]

            price_text = item.select(".price")[0].text.strip()
            price = parse_price(price_text)

            address = item.select_one(".address").text.strip()

            # детали
            rooms, area, floor, total_floors = parse_details(title)

            price_per_m2 = None
            if price and area:
                price_per_m2 = round(price / area, 2)

            # изображения
            images = []
            for img in item.select("img"):
                src = img.get("data-src")
                if src:
                    images.append(src)

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
                "district": None,  # потом можно распарсить
                "source": "house",
                "link": link,
                "images": images,
            })

        except Exception as e:
            print("Ошибка:", e)
            continue

    return flats


if __name__ == "__main__":
    data = parse_house()

    # вывод
    print(json.dumps(data[:3], indent=2, ensure_ascii=False))

    # сохранить в файл
    with open("../../flats.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)