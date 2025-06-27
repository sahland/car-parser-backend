import os
import re
import time
import json
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.brand_utils import extract_brand
from utils.currency import get_krw_to_rub_rate
from utils.parser_helpers import normalize_mileage

# 🔤 Словарь перевода моделей
model_translation = {
    "쏘렌토": "Sorento",
    "투싼": "Tucson",
    "레이": "Ray",
    "카니발": "Carnival",
    "코나": "Kona",
    "셀토스": "Seltos",
    "모닝": "Morning",
    "K3": "K3",
    "K5": "K5",
    "K7": "K7",
    "K8": "K8",
    "아반떼": "Avante",
    "그랜저": "Grandeur",
    "싼타페": "Santa Fe",
    "제네시스": "Genesis",
    "스토닉": "Stonic",
    "QM3": "QM3",
    "QM5": "QM5",
    "QM6": "QM6",
    "SM3": "SM3",
    "SM5": "SM5",
    "SM6": "SM6",
    "SM7": "SM7",
    "트랙스": "Trax",
    "스파크": "Spark",
    "말리부": "Malibu",
    "올란도": "Orlando",
    "크루즈": "Cruze",
    "임팔라": "Impala",
    "티볼리": "Tivoli",
    "렉스턴": "Rexton",
    "코란도": "Korando",
    "G70": "G70",
    "G80": "G80",
    "G90": "G90",
    "GV70": "GV70",
    "GV80": "GV80",
    "베뉴": "Venue",
    "아이오닉": "Ioniq",
    "아이오닉5": "Ioniq 5",
    "아이오닉6": "Ioniq 6",
    "넥쏘": "Nexo",
    "벨로스터": "Veloster",
    "펠리세이드": "Palisade",
    "맥스크루즈": "Maxcruz",
    "i30": "i30",
    "i40": "i40",
    "엑센트": "Accent",
    "베르나": "Verna",
    "아슬란": "Aslan",
    "티볼리 에어": "Tivoli Air",
    "티볼리 XLV": "Tivoli XLV",
    "토레스": "Torres",
    "렉스턴 스포츠": "Rexton Sports",
    "렉스턴 스포츠 칸": "Rexton Sports Khan",
    "코란도 투리스모": "Korando Turismo"
}



def extract_engine_volume(text):
    match = re.search(r"\b(\d\.\d\s?(?:T|Turbo)?)\b", text, re.IGNORECASE)
    return match.group(1).replace(" ", "") if match else "—"


def extract_fuel_type(text):
    fuel_keywords = {
        "Gasoline": ["Gasoline", "가솔린", "휘발유"],
        "Diesel": ["Diesel", "디젤"],
        "LPG": ["LPG", "Lpi", "엘피지"],
        "Hybrid": ["Hybrid", "하이브리드"],
        "Electric": ["EV", "Electric", "전기"],
    }
    for fuel, patterns in fuel_keywords.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return fuel
    return "—"


def extract_model_name(title, brand):
    title = title.replace(brand, "").strip()
    for kor_name in model_translation:
        if kor_name in title:
            return model_translation[kor_name]
    return title.split()[0]  # fallback


def extract_year(data_line):
    # ищем "(19년형)" или "19/01식(19년형)"
    match = re.search(r"\(?(\d{2})년형\)?", data_line)
    if match:
        year = int(match.group(1))
        return f"20{year}" if year <= 25 else f"19{year}"
    return ""

def extract_mileage(data_line):
    match = re.search(r"([\d,]+)\s?km", data_line)
    if match:
        return normalize_mileage(match.group(1).replace(",", ""))
    return "—"

def extract_image_url(card):
    try:
        return card.find_element(By.CSS_SELECTOR, ".thumnail img").get_attribute("src")
    except Exception:
        return "—"

def parse_kbchachacha(pages=5):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    krw_rate = get_krw_to_rub_rate()
    cars_data = []

    driver.get("https://www.kbchachacha.com/public/search/main.kbc")
    time.sleep(5)

    for page in range(1, pages + 1):
        print(f"🌐 Страница {page}")
        js = f"window.location.href = 'https://www.kbchachacha.com/public/search/main.kbc#!?page={page}&sort=-orderDate';"
        driver.execute_script(js)
        time.sleep(5)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.area"))
            )
        except Exception as e:
            print(f"❌ Ошибка на странице {page}: {e}")
            continue

        cards = driver.find_elements(By.CSS_SELECTOR, "div.area")
        print(f"✅ Найдено {len(cards)} автомобилей")

        for card in cards:
            try:
                title_raw = card.find_element(By.CSS_SELECTOR, "strong.tit").text.strip()
                price_text = card.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                price_krw = int(re.sub(r"[^\d]", "", price_text))
                price_rub = round(price_krw * 10000 * krw_rate)

                brand = extract_brand(title_raw, source="kbchachacha")
                name = extract_model_name(title_raw, brand)
                data_line = card.find_element(By.CSS_SELECTOR, "div.data-line").text
                year = extract_year(data_line)
                mileage = extract_mileage(data_line)
                engine_volume = extract_engine_volume(title_raw)
                fuel_type = extract_fuel_type(title_raw)
                image = extract_image_url(card)

                car = {
                    "name": name,
                    "brand": brand,
                    "year": year,
                    "price": price_rub,
                    "price_krw": price_krw,
                    "krw_to_rub": krw_rate,
                    "mileage": mileage,
                    "fuel_type": fuel_type,
                    "power": "—",
                    "drive": "—",
                    "engine_volume": engine_volume,
                    "image": image
                }

                cars_data.append(car)

            except Exception as e:
                print("❌ Ошибка при обработке машины:", e)

    driver.quit()

    # Сохраняем JSON
    os.makedirs("json_data/kbchachacha", exist_ok=True)
    with open("json_data/kbchachacha/kbchachacha_all.json", "w", encoding="utf-8") as f:
        json.dump(cars_data, f, ensure_ascii=False, indent=2)

    # Группировка по брендам
    grouped = defaultdict(list)
    for car in cars_data:
        grouped[car["brand"]].append(car)

    os.makedirs("export/kbchachacha", exist_ok=True)
    for brand, group in grouped.items():
        safe_brand = brand.replace("/", "_")
        with open(f"export/kbchachacha/{safe_brand}.json", "w", encoding="utf-8") as f:
            json.dump(group, f, ensure_ascii=False, indent=2)

    print(f"✅ Сохранено {len(cars_data)} авто в JSON")
    return cars_data
