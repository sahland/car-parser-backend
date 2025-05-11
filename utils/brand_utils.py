import json

with open("json_data/car_brands_by_country.json", encoding="utf-8") as f:
    brand_ref = json.load(f)
ALL_BRANDS = set(brand_ref["all_brands"])

with open("json_data/che168/hieroglyph_brand_map_che168.json", encoding="utf-8") as f:
    CHE168_MAP = json.load(f)

with open("json_data/encar/hieroglyph_brand_map_encar.json", encoding="utf-8") as f:
    ENCAR_MAP = json.load(f)

def extract_brand(name: str, source: str = "che168"):
    name_clean = name.lower()
    MAP = CHE168_MAP if source == "che168" else ENCAR_MAP

    for cn, en in MAP.items():
        if cn in name:
            return en
    for known in ALL_BRANDS:
        if known.lower() in name_clean:
            return known
    with open("unknown_brands.txt", "a", encoding="utf-8") as log:
        log.write(name + "\n")
    return "Other"