import json
import os
from urllib.parse import urlparse

INPUT_FILE_1 = './json_data/encar/encar_rendered.json'
INPUT_FILE_2 = './json_data/kbchachacha/kbchachacha_all.json'
OUTPUT_FILE = 'car_catalog_encar.html'
PLACEHOLDER_IMAGE = "https://via.placeholder.com/300x200?text=No+Image"
ITEMS_PER_PAGE = 10
CATALOG_TITLE = "Каталог автомобилей из Южной Кореи"

# Чтение обоих файлов
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    print(f"❌ Файл не найден: {file_path}")
    return []

cars_1 = load_json(INPUT_FILE_1)
cars_2 = load_json(INPUT_FILE_2)

# Объединяем оба списка
cars = cars_1 + cars_2

# Удаляем некорректные объекты без названия или цены
cars = [car for car in cars if car.get("name") and isinstance(car.get("price"), (int, float))]

for car in cars:
    image_url = car.get("image", "")
    
    if image_url and "noimage" not in image_url:
        # Удаляем протокол
        parsed_url = urlparse(image_url)
        netloc_and_path = parsed_url.netloc + parsed_url.path

        # Удаляем query (если есть) и добавляем .jpg в конце (или оставляем как есть, если расширение другое)
        if '.' in netloc_and_path:
            ext = netloc_and_path.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                ext = 'jpg'
        else:
            ext = 'jpg'

        final_url = f"https://images.weserv.nl/?url={netloc_and_path}"
        car["image"] = final_url
    else:
        car["image"] = PLACEHOLDER_IMAGE

# Получаем список брендов
brands = sorted(set(car.get('brand', 'Other') for car in cars))

# Генерация HTML (оставим как есть, переменная `json_data` просто заменяется)
json_data = json.dumps(cars, ensure_ascii=False)
brand_list_html = '\n'.join(f'<li onclick="filterBrand(\'{b}\')">{b}</li>' for b in brands)

html_block = f'''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>{CATALOG_TITLE}</title>
</head>
<body>
<!-- BEGIN: Sidebar Car Catalog -->
<div class="catalog-wrapper-white">
  <h1 class="catalog-title-white">{CATALOG_TITLE}</h1>
  <p style="text-align:center; font-size:14px; color:gray; margin: 0 0 30px;">
    Цены указаны без учета доставки, пошлин и регистрации
  </p>
  <div class="catalog-container-white">
    <aside class="sidebar-white">
      <h3>Бренды</h3>
      <ul class="brand-list-white">
        <li onclick="filterBrand('all')" class="active">Все</li>
        {brand_list_html}
      </ul>
    </aside>
    <main class="main-content-white">
      <div id="car-container-white" class="car-container-white"></div>
      <div id="pagination-white" class="pagination-white"></div>
    </main>
  </div>
</div>

<div id="car-popup-white" class="popup-overlay-white" style="display: none;">
  <div class="popup-content-white">
    <span class="popup-close-white" onclick="closePopupWhite()">&times;</span>
    <div class="popup-car-info-white">
      <div class="popup-image-white" id="popup-image-white"></div>
      <h2 id="popup-name-white"></h2>
      <p><strong>Год:</strong> <span id="popup-year-white"></span></p>
      <p><strong>Пробег:</strong> <span id="popup-mileage-white"></span></p>
      <p><strong>Топливо:</strong> <span id="popup-fuel-white"></span></p>
      <p><strong>Цена:</strong> <span id="popup-price-white"></span></p>
    </div>
    <form id="order-form-white" onsubmit="sendToTildaCRMWhite(event)">
      <input type="text" name="name" placeholder="Ваше имя" required />
      <input type="tel" name="phone" placeholder="Телефон" required />
      <input type="hidden" name="car_name" id="form-car-name" />
      <input type="hidden" name="car_fuel" id="form-car-fuel" />
      <input type="hidden" name="car_price" id="form-car-price" />
      <button type="submit">Заказать автомобиль</button>
    </form>
    <form id="tilda-hidden-form"
          action="https://forms.tildacdn.com/proccess/?projectid=12400529&pageid=67516763"
          method="POST"
          style="display: none;">
      <input type="hidden" name="formname" value="Заказ авто" />
      <input type="hidden" name="name" />
      <input type="hidden" name="phone" />
      <input type="hidden" name="car_name" />
      <input type="hidden" name="car_fuel" />
      <input type="hidden" name="car_price" />
    </form>
  </div>
</div>

<script>
(function () {{
  const allCarsWhite = { json_data };
  let currentBrandWhite = "all";
  let currentPageWhite = 1;

  function getItemsPerPageWhite() {{
    return window.innerWidth <= 768 ? 4 : 10;
  }}

  function filterBrandWhite(brand) {{
    currentBrandWhite = brand;
    currentPageWhite = 1;
    document.querySelectorAll('.brand-list-white li').forEach(el => el.classList.remove('active'));
    const activeItem = Array.from(document.querySelectorAll('.brand-list-white li')).find(el => el.textContent === brand || (brand === 'all' && el.textContent === 'Все'));
    if (activeItem) activeItem.classList.add('active');
    renderCatalogWhite();
  }}

  window.filterBrandWhite = filterBrandWhite; // делаем функцию доступной из HTML
  window.filterBrand = filterBrandWhite;

  function openPopupWhite(car) {{
    document.getElementById("popup-name-white").textContent = car.name;
    document.getElementById("popup-year-white").textContent = car.year;
    document.getElementById("popup-mileage-white").textContent = car.mileage;
    document.getElementById("popup-fuel-white").textContent = car.fuel_type || '—';
    document.getElementById("popup-price-white").textContent = car.price.toLocaleString() + " ₽";
    document.getElementById("popup-image-white").style.backgroundImage = `url('${{car.image}}')`;

    document.getElementById("form-car-name").value = car.name;
    document.getElementById("form-car-fuel").value = car.fuel_type || '—';
    document.getElementById("form-car-price").value = car.price;

    document.getElementById("car-popup-white").style.display = "flex";
  }}

  window.closePopupWhite = function () {{
    document.getElementById("car-popup-white").style.display = "none";
  }};

  function sendToTildaCRMWhite(e) {{
    e.preventDefault();

    const name = e.target.name.value;
    const phone = e.target.phone.value;
    const carName = e.target['car_name'].value;
    const carFuel = e.target['car_fuel'].value;
    const carPrice = e.target['car_price'].value;

    const formData = new FormData();
    formData.append('formname', 'Заказ авто');
    formData.append('name', name);
    formData.append('phone', phone);
    formData.append('car_name', carName);
    formData.append('car_fuel', carFuel);
    formData.append('car_price', carPrice);

    fetch('https://auto-east.tilda.ws/customized_cars', {{
      method: 'POST',
      body: formData,
      mode: 'no-cors'
    }});

    alert('✅ Заявка отправлена!');
    closePopupWhite();
  }}

  window.sendToTildaCRMWhite = sendToTildaCRMWhite;

  function renderCatalogWhite() {{
    const container = document.getElementById("car-container-white");
    container.innerHTML = "";

    const itemsPerPage = getItemsPerPageWhite();
    const filtered = currentBrandWhite === "all" ? allCarsWhite : allCarsWhite.filter(c => c.brand === currentBrandWhite);
    const totalPages = Math.ceil(filtered.length / itemsPerPage);
    const start = (currentPageWhite - 1) * itemsPerPage;
    const visibleCars = filtered.slice(start, start + itemsPerPage);

    visibleCars.forEach((car, index) => {{
      const card = document.createElement("div");
      card.className = "car-card-white";
      card.style.animationDelay = `${{index * 100}}ms`;
      card.onclick = () => openPopupWhite(car);
      card.innerHTML = `
        <div class="car-image-white"><div class="loader-white"></div></div>
        <div class="car-info-white">
          <h3>${{car.name}}</h3>
          <p><strong>Год:</strong> ${{car.year}}</p>
          <p><strong>Пробег:</strong> ${{car.mileage}}</p>
          <p><strong>Топливо:</strong> ${{car.fuel_type || '—'}}</p>
          <p class="price"><strong>${{car.price.toLocaleString()}} ₽</strong></p>
        </div>
      `;
      const img = new Image();
      img.src = car.image;
      img.onload = () => {{
        card.querySelector('.car-image-white').style.backgroundImage = `url('${{car.image}}')`;
        card.querySelector('.loader-white').style.display = 'none';
      }};
      container.appendChild(card);
    }});

    const pagination = document.getElementById("pagination-white");
    pagination.innerHTML = "";
    if (totalPages > 1) {{
      for (let i = 1; i <= totalPages; i++) {{
        const link = document.createElement("a");
        link.href = "#";
        link.innerText = i;
        link.className = i === currentPageWhite ? "active" : "";
        link.onclick = function (e) {{
          e.preventDefault();
          currentPageWhite = i;
          renderCatalogWhite();
        }};
        pagination.appendChild(link);
      }}
    }}
  }}
  renderCatalogWhite();
}})();
</script>


<style>
body {{
  margin: 0;
  background: #ffffff;
  font-family: 'Segoe UI', sans-serif;
  color: black;
}}

.catalog-title-white {{
  text-align: center;
  font-size: 36px;
  color: black;
  margin: 40px 0 20px;
  font-weight: bold;
}}

.catalog-container-white {{
  display: flex;
  flex-grow: 1;
  align-items: flex-start;
}}

.sidebar-white {{
  width: 220px;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 60vh;
  color: black;
}}

.sidebar-white h3 {{
  text-align: center;
  font-size: 16px;
  margin: 0;
  padding: 0;
  font-weight: bold;
  color: black;
}}

.catalog-wrapper-white {{
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}}

.brand-list-white {{
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding: 0;
  margin: 0;
  list-style: none;
  scrollbar-width: thin;
  max-height: 70vh;
}}

.brand-list-white li {{
  padding: 6px 12px;
  background: #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  color: black;
  text-align: center;
  white-space: nowrap;
}}

.brand-list-white li:hover,
.brand-list li.active {{
  background: black;
  color: white;
}}

.main-content-white {{
  flex-grow: 1;
  padding: 20px;
}}

.car-container-white {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}}

.car-card-white {{
  opacity: 0;
  animation: fadeInUp 0.5s ease forwards;
  background: #fafafa;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}}

.car-card-white:hover {{
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}}

.car-image-white {{
  width: 100%;
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
}}

.loader-white {{
  border: 4px solid rgba(0, 0, 0, 0.2);
  border-top: 4px solid black;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  position: absolute;
  top: calc(50% - 15px);
  left: calc(50% - 15px);
}}

@keyframes fadeInUp {{
  0% {{
    opacity: 0;
    transform: translateY(20px);
  }}
  100% {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

@keyframes spin {{
  0% {{ transform: rotate(0deg); }}
  100% {{ transform: rotate(360deg); }}
}}

.car-info-white {{
  padding: 16px;
}}

.car-info-white h3 {{
  margin: 0 0 10px;
  font-size: 17px;
  color: black;
}}

.car-info-white p {{
  margin: 4px 0;
  font-size: 14px;
  color: #555;
}}

.car-info-white .price {{
  color: #d60000;
  font-weight: bold;
  font-size: 16px;
  margin-top: 10px;
}}

.pagination-white {{
  margin-top: 30px;
  text-align: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}}

.pagination-white a {{
  background: #f0f0f0;
  color: black;
  padding: 8px 14px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  font-size: 14px;
  min-width: 36px;
  text-align: center;
}}

.pagination-white a.active {{
  background: black;
  color: white;
}}

.popup-overlay-white {{
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}}

.popup-content-white {{
  background: #fff;
  color: #000;
  padding: 20px;
  border-radius: 15px;
  width: 90%;
  max-width: 400px;
  position: relative;
}}

.popup-close-white {{
  position: absolute;
  top: 10px; right: 15px;
  font-size: 24px;
  cursor: pointer;
}}

.popup-image-white {{
  width: 100%;
  height: 180px;
  background-size: cover;
  background-position: center;
  border-radius: 12px;
  margin-bottom: 16px;
}}

#order-form-white input {{
  width: 100%;
  background: white !important;
  color: black;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px;
  font-size: 16px;
  margin-top: 10px;
  box-sizing: border-box;
}}

#order-form-white input:focus {{
  outline: none;
  border-color: black;
}}

#order-form-white button {{
  width: 100%;
  background-color: black !important;
  color: white !important;
  font-weight: bold;
  border: none;
  border-radius: 8px;
  padding: 12px;
  margin-top: 16px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s ease;
  box-sizing: border-box;
}}

#order-form-white button:hover {{
  background-color: #333 !important;
}}

@media (max-width: 768px) {{
  .catalog-container-white {{
    flex-direction: column;
  }}

  .sidebar-white {{
    width: 100%;
    max-height: none;
    padding: 10px 0;
    border-radius: 0;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    overflow-x: auto;
    overflow-y: hidden;
  }}

  .sidebar-white h3 {{
    display: none;
  }}

  .brand-list-white {{
    flex-direction: row;
    max-height: none;
    padding: 0 10px;
  }}

  .brand-list-white li {{
    flex-shrink: 0;
    font-size: 13px;
    scroll-snap-align: start;
  }}

  .car-container-white {{
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }}

  .car-card-white {{
    font-size: 12px;
    border-radius: 10px;
  }}

  .car-image-white {{
    height: 120px;
  }}

  .car-info-white h3 {{
    font-size: 14px;
  }}

  .car-info-white p {{
    font-size: 12px;
  }}

  .car-info-white .price {{
    font-size: 14px;
  }}
}}
</style>
<!-- END: Sidebar Car Catalog -->
</body>
</html>
'''

with open(OUTPUT_FILE, 'w', encoding='utf-8-sig') as f:
    f.write(html_block)

print(f"✅ HTML saved to '{OUTPUT_FILE}'")
