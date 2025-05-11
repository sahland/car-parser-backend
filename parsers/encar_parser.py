import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.selenium_setup import get_driver
from utils.brand_utils import extract_brand
from utils.currency import get_krw_to_rub_rate
from utils.parser_helpers import clean_display_name, normalize_mileage

def parse_encar():
    driver = get_driver(headless=False)
    krw_rate = get_krw_to_rub_rate()
    cars_data = []

    for page in range(1, 11):
        if not driver.window_handles:
            print("❌ Окно браузера закрыто. Прерываю парсинг.")
            break

        url = f"https://www.encar.com/dc/dc_carsearchlist.do?page={page}"
        print(f"🌐 Открываю страницу {page}: {url}")
        driver.get(url)
        time.sleep(3)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='list_row']"))
            )
        except:
            print(f"❌ Машины не найдены на странице {page}.")
            continue

        cards = driver.find_elements(By.XPATH, "//div[@class='list_row']")
        for card in cards:
            try:
                strong_tags = card.find_elements(By.TAG_NAME, "strong")
                title = strong_tags[0].text.strip() if strong_tags else "—"

                year_km = "—"
                try:
                    year_km = card.find_element(By.CLASS_NAME, "year").text.strip()
                except:
                    pass

                try:
                    price_text = card.find_element(By.CLASS_NAME, "price").text.strip()
                except:
                    price_text = ""

                try:
                    img_tag = card.find_element(By.CSS_SELECTOR, "td.img img")
                    image = img_tag.get_attribute("src") if img_tag else ""
                except:
                    image = ""

                brand = extract_brand(title, source="encar")
                name = clean_display_name(title)

                year = year_km.split("/")[0].strip() if "/" in year_km else "—"
                mileage = normalize_mileage(year_km.split("/")[1].strip()) if "/" in year_km else "—"

                price_krw = int(re.sub(r"[^0-9]", "", price_text)) if price_text else 0
                price_rub = round(price_krw * krw_rate)

                car = {
                    "name": name,
                    "brand": brand,
                    "year": year,
                    "price": price_rub,
                    "price_krw": price_krw,
                    "krw_to_rub": krw_rate,
                    "mileage": mileage,
                    "fuel_type": "—",
                    "power": "—",
                    "drive": "—",
                    "engine_volume": "—",
                    "image": image
                }
                cars_data.append(car)
            except Exception as e:
                print("❌ Ошибка при карточке:", e)

    driver.quit()
    print(f"🔍 Спарсено {len(cars_data)} автомобилей с Encar")
    return cars_data