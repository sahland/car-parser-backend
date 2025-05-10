import time
import json
import os
import re
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.selenium_setup import get_driver
from utils.parser_helpers import *
from utils.brand_utils import extract_brand
from utils.currency import get_cny_to_rub_rate

def parse_che168_selenium():
    driver = get_driver(headless=False)
    driver.get("https://m.che168.com/beijing/list/")
    input("⏳ Прокрути вручную и нажми Enter для продолжения...")

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@style,'flex-direction: row')]"))
        )
    except:
        print("❌ Карточки не найдены")
        driver.quit()
        return []

    yuan_rate = get_cny_to_rub_rate()
    cars_data = []
    for card in driver.find_elements(By.XPATH, "//div[contains(@style,'flex-direction: row')]"):
        text = card.text.strip()
        if not re.search(r"\d{4}年.*?公里", text):
            continue

        try:
            image_els = card.find_elements(By.TAG_NAME, "img")
            image = image_els[0].get_attribute("src") if image_els else ""

            name_raw = clean_name(text)
            name = clean_display_name(name_raw)
            brand = extract_brand(text)

            parts = text.split("\n")
            mileage_block = next((part for part in parts if "/" in part), "")
            year = normalize_year(mileage_block.split("/")[0].strip()) if "/" in mileage_block else "—"
            mileage = normalize_mileage(mileage_block.split("/")[1].strip()) if "/" in mileage_block else "—"

            price_match = re.findall(r"(\d+(?:\.\d+)?)\s*万", text)
            raw_price_yuan = float(price_match[-1]) if price_match else 0
            price_yuan_val = raw_price_yuan * 10000

            car = {
                "name": name,
                "brand": brand,
                "year": year,
                "price": round(price_yuan_val * yuan_rate),
                "price_yuan": round(raw_price_yuan, 2),
                "yuan_to_rub": yuan_rate,
                "mileage": mileage,
                "fuel_type": "—",
                "power": "—",
                "drive": "—",
                "engine_volume": "2.0",
                "image": image
            }
            cars_data.append(car)
        except Exception as e:
            print("❌ Ошибка при карточке:", e)

    driver.quit()
    print(f"🔍 Найдено {len(cars_data)} автомобилей через Selenium")
    return cars_data