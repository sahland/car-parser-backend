import re

JUNK_WORDS = {"诚信车", "精品车", "Boutique", "World", "Целостный", "Viagra", "车"}

def clean_name(raw_name: str):
    for junk in JUNK_WORDS:
        raw_name = raw_name.replace(junk, "")
    return raw_name.strip()

def clean_display_name(text):
    no_chinese = re.sub(r'[\u4e00-\u9fff]+', '', text)
    cut = re.split(r'[\\/¥]', no_chinese)[0]
    return cut.strip()

def normalize_year(raw: str):
    return raw.replace("年", "").strip().replace("未上牌", "2024")

def normalize_mileage(raw: str):
    raw = raw.replace("公里", " км").replace("km", " км").replace("KM", " км")
    if "万" in raw:
        try:
            km = float(re.sub(r"[^0-9.]", "", raw)) * 10000
            return f"{int(km):,} км".replace(",", " ")
        except:
            return raw
    return raw.strip()