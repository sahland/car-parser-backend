import time
import re

from googletrans import Translator

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.brand_utils import extract_brand
from utils.currency import get_krw_to_rub_rate
from utils.parser_helpers import normalize_mileage

def parse_encar():

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    translator = Translator()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    krw_rate = get_krw_to_rub_rate()
    cars_data = []

    for page in range(1, 11):
        if not driver.window_handles:
            print("❌ Окно браузера закрыто. Прерываю парсинг.")
            break

        url = f"http://www.encar.com/fc/fc_carsearchlist.do?carType=for#!%7B%22action%22%3A%22(And.Hidden.N._.CarType.N.)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22ModifiedDate%22%2C%22page%22%3A{page}%2C%22limit%22%3A20%2C%22searchKey%22%3A%22%22%2C%22loginCheck%22%3Afalse%7D"
        print(f"🌐 Открываю страницу {page}: {url}")
        driver.get(url)
        time.sleep(3)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//tbody[@id='sr_normal']/tr"))
            )
        except:
            print(f"❌ Машины не найдены на странице {page}.")
            continue

        rows = driver.find_elements(By.XPATH, "//tbody[@id='sr_normal']/tr")
        for row in rows:
            try:
                # Извлечение данных из строки
                title = row.find_element(By.XPATH, ".//td[@class='inf']/a/span[@class='cls']").text.strip()
                year = row.find_element(By.XPATH, ".//td[@class='inf']/span[@class='detail']/span[@class='yer']").text.strip()
                mileage = row.find_element(By.XPATH, ".//td[@class='inf']/span[@class='detail']/span[@class='km']").text.strip()
                fuel_type = row.find_element(By.XPATH, ".//td[@class='inf']/span[@class='detail']/span[@class='fue']").text.strip()
                price_text = row.find_element(By.XPATH, ".//td[@class='prc_hs']/strong").text.strip()
                img_element = row.find_element(By.XPATH, ".//td[@class='img']/div/a/span/img")
                image = img_element.get_attribute("data-src") or img_element.get_attribute("src")


                brand = extract_brand(title, source="encar")
                year = '20' + year.split('/')[0]
                mileage = normalize_mileage(mileage)

                price_krw = int(re.sub(r"[^0-9]", "", price_text)) if price_text else 0
                price_rub = round(price_krw *  10_000 * krw_rate)

                car = {
                    "name": title,
                    "brand": brand,
                    "year": year,
                    "price": price_rub,
                    "price_krw": price_krw,
                    "krw_to_rub": krw_rate,
                    "mileage": mileage,
                    "fuel_type": fuel_type,
                    "power": "—",
                    "drive": "—",
                    "engine_volume": "—",
                    "image": image
                }
                cars_data.append(car)
            except Exception as e:
                print("❌ Ошибка при обработке строки:", e)
        
    for car in cars_data:
        try:
            if not car['name']:
                print("❌ Название автомобиля отсутствует.")
                cars_data.remove(car)
                continue
            car['name'] = translator.translate(car['name'], src='ko', dest='en').text
            car['fuel_type'] = translator.translate(car['fuel_type'], src='ko', dest='ru').text

        except Exception as e:
            print("❌ Ошибка при переводе:", e)

    driver.quit()
    print(f"🔍 Спарсено {len(cars_data)} автомобилей с Encar")
    return cars_data