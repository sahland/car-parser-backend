import os
import json
from collections import defaultdict
from parsers.encar_parser import parse_encar

result = parse_encar()
if result:
    os.makedirs("json_data/encar", exist_ok=True)
    with open("json_data/encar/encar_rendered.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    grouped = defaultdict(list)
    for car in result:
        grouped[car["brand"].strip()].append(car)

    os.makedirs("export/encar", exist_ok=True)
    for brand, cars in grouped.items():
        safe_brand = brand.replace("/", "_")
        with open(f"export/encar/{safe_brand}.json", "w", encoding="utf-8") as f:
            json.dump(cars, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(result)} cars grouped by brand to export/encar")
else:
    print("❌ No data parsed from Encar.")