import time
import json
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from utils.selenium_setup import get_driver
from utils.parser_helpers import *
from utils.brand_utils import extract_brand
from utils.currency import get_cny_to_rub_rate

def parse_che168_selenium():
    driver = get_driver(headless=False)
    driver.get("https://m.che168.com/beijing/list/")

    # Ждём, пока появятся первые карточки
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@style,'flex-direction: row')]"))
        )
    except:
        print("❌ Карточки не найдены")
        driver.quit()
        return []

    # Улучшенная прокрутка
    scroll_pause_time = 3
    max_scroll_attempts = 50
    previous_card_count = 0
    attempts_without_new_cards = 0

    while attempts_without_new_cards < 5:
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(scroll_pause_time)

        cards = driver.find_elements(By.XPATH, "//div[contains(@style,'flex-direction: row')]")
        current_card_count = len(cards)
        print(f"🔎 Прокрутка: найдено {current_card_count} карточек")

        if current_card_count == previous_card_count:
            attempts_without_new_cards += 1
            print(f"⚠️ Новых карточек не появилось ({attempts_without_new_cards}/5)")
        else:
            attempts_without_new_cards = 0

        previous_card_count = current_card_count

        if attempts_without_new_cards >= 5:
            print("✅ Прокрутка завершена: новых карточек больше нет")
            break

    # Собираем данные с карточек
    yuan_rate = get_cny_to_rub_rate()
    cars_data = []

    cards = driver.find_elements(By.XPATH, "//div[contains(@style,'flex-direction: row')]")
    print(f"🔎 Итоговое количество карточек: {len(cards)}")

    for card in cards:
        text = card.text.strip()
        # Проверяем наличие цены
        price_match = re.search(r"(\d+(?:\.\d+)?)\s*万", text)
        if not price_match:
            print(f"Исключена карточка без цены: {text}")
            continue

        # Проверяем наличие имени автомобиля (хотя бы 2 китайских иероглифа или латинские буквы)
        name_match = re.search(r"[一-龥]{2,}|[\w\s-]{3,}", text)
        if not name_match:
            print(f"Исключена карточка без имени: {text}")
            continue

        try:
            image_els = card.find_elements(By.TAG_NAME, "img")
            image = image_els[0].get_attribute("src") if image_els else ""
            # Исключаем карточки без изображения или с заглушкой
            if not image or "collect_grey" in image:
                print(f"Исключена карточка без изображения: {text}")
                continue

            name_raw = clean_name(text)
            name = clean_display_name(name_raw)
            brand = extract_brand(text, source="che168")

            parts = text.split("\n")
            mileage_block = next((part for part in parts if "/" in part and "年" in part), "")
            if mileage_block:
                year = normalize_year(mileage_block.split("/")[0].strip()) if "/" in mileage_block else "—"
                mileage = normalize_mileage(mileage_block.split("/")[1].strip()) if "/" in mileage_block else "—"
            else:
                year = "—"
                mileage = "—"

            raw_price_yuan = float(price_match.group(1))
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
            print(f"❌ Ошибка при обработке карточки: {e}")

    driver.quit()
    print(f"✅ Найдено {len(cars_data)} автомобилей через Selenium")
    return cars_data