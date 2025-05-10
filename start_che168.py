from parsers.che168_parser import parse_che168_selenium
import json
import os
from collections import defaultdict

result = parse_che168_selenium()
if result:
    os.makedirs("json_data/che168", exist_ok=True)
    with open("json_data/che168/che168_rendered.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    grouped = defaultdict(list)
    for car in result:
        grouped[car["brand"].strip()].append(car)

    os.makedirs("export/che168", exist_ok=True)
    for brand, cars in grouped.items():
        safe_brand = brand.replace("/", "_")
        with open(f"export/che168/{safe_brand}.json", "w", encoding="utf-8") as f:
            json.dump(cars, f, ensure_ascii=False, indent=2)

    print(f"✅ Сохранено {len(result)} авто и сгруппировано по маркам в папке export")
else:
    print("❌ Данные не получены.")