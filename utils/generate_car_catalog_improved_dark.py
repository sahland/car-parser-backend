import json
import os

INPUT_FILE = './json_data/che168/che168_rendered.json'
OUTPUT_FILE = 'car_catalog_che168.html'
ITEMS_PER_PAGE = 10
CATALOG_TITLE = "Каталог автомобилей из Китая"

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    cars = json.load(f)

brands = sorted(set(car.get('brand', 'Other') for car in cars))

# Проксируем изображения через images.weserv.nl
for car in cars:
    if car.get("image"):
        raw_url = car["image"].replace("https://", "").replace("http://", "")
        car["image"] = f"https://images.weserv.nl/?url={raw_url}"

json_data = json.dumps(cars, ensure_ascii=False)
brand_list_html = '\n'.join(f'<li onclick="filterBrand(\'{b}\')">{b}</li>' for b in brands)

html_block = f'''
<!-- BEGIN: Sidebar Car Catalog -->
<div class="catalog-wrapper">
  <h1 class="catalog-title">{CATALOG_TITLE}</h1>
  <p style="text-align:center; font-size:14px; color:white; margin: 0 0 30px;">
    Цены указаны без учета доставки, пошлин и регистрации
  </p>
  <div class="catalog-container">
    <aside class="sidebar">
      <h3>Бренды</h3>
      <ul class="brand-list">
        <li onclick="filterBrand('all')" class="active">Все</li>
        {brand_list_html}
      </ul>
    </aside>
    <main class="main-content">
      <div id="car-container" class="car-container"></div>
      <div id="pagination" class="pagination"></div>
    </main>
  </div>
</div>

<div id="car-popup" class="popup-overlay" style="display: none;">
  <div class="popup-content">
    <span class="popup-close" onclick="closePopup()">&times;</span>
    <div class="popup-car-info">
      <div class="popup-image" id="popup-image"></div>
      <h2 id="popup-name"></h2>
      <p><strong>Год:</strong> <span id="popup-year"></span></p>
      <p><strong>Пробег:</strong> <span id="popup-mileage"></span></p>
      <p><strong>Цена:</strong> <span id="popup-price"></span></p>
    </div>
    <form id="order-form" onsubmit="sendToTildaCRM(event)">
      <input type="text" name="name" placeholder="Ваше имя" required />
      <input type="tel" name="phone" placeholder="Телефон" required />
      <input type="hidden" name="car_name" id="form-car-name" />
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
      <input type="hidden" name="car_price" />
    </form>
  </div>
</div>

<script>
const allCars = {json_data};
let currentBrand = "all";
let currentPage = 1;
const itemsPerPage = getItemsPerPage(); // переместить внутрь функции

function getItemsPerPage() {{
  return window.innerWidth <= 768 ? 4 : 10;
}}

function filterBrand(brand) {{
  currentBrand = brand;
  currentPage = 1;
  document.querySelectorAll('.brand-list li').forEach(el => el.classList.remove('active'));
  const activeItem = Array.from(document.querySelectorAll('.brand-list li')).find(el => el.textContent === brand || (brand === 'all' && el.textContent === 'Все'));
  if (activeItem) activeItem.classList.add('active');
  renderCatalog();
}}

function sendToTildaCRM(e) {{
  e.preventDefault();

  const name = e.target.name.value;
  const phone = e.target.phone.value;
  const carName = e.target['car_name'].value;
  const carPrice = e.target['car_price'].value;

  const formData = new FormData();
  formData.append('formname', 'Заказ авто');
  formData.append('name', name);
  formData.append('phone', phone);
  formData.append('car_name', carName);
  formData.append('car_price', carPrice);

  fetch('https://auto-east.tilda.ws/customized_cars', {{
    method: 'POST',
    body: formData,
    mode: 'no-cors'
  }});

  alert('✅ Заявка отправлена!');
  closePopup();
}};

function openPopup(car) {{
  document.getElementById("popup-name").textContent = car.name;
  document.getElementById("popup-year").textContent = car.year;
  document.getElementById("popup-mileage").textContent = car.mileage;
  document.getElementById("popup-price").textContent = car.price.toLocaleString() + " ₽";
  document.getElementById("popup-image").style.backgroundImage = `url('${{car.image}}')`;

  document.getElementById("form-car-name").value = car.name;
  document.getElementById("form-car-price").value = car.price;

  document.getElementById("car-popup").style.display = "flex";
}}

function closePopup() {{
  document.getElementById("car-popup").style.display = "none";
}}

function renderCatalog() {{
  const container = document.getElementById("car-container");
  container.innerHTML = "";

  const itemsPerPage = getItemsPerPage();
  const filtered = currentBrand === "all" ? allCars : allCars.filter(c => c.brand === currentBrand);
  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const start = (currentPage - 1) * itemsPerPage;
  const visibleCars = filtered.slice(start, start + itemsPerPage);

  visibleCars.forEach((car, index) => {{
    const card = document.createElement("div");
    card.className = "car-card";
    card.style.animationDelay = `${{index * 100}}ms`;
    card.onclick = () => openPopup(car);
    card.innerHTML = `
      <div class="car-image"><div class="loader"></div></div>
      <div class="car-info">
        <h3>${{car.name}}</h3>
        <p><strong>Год:</strong> ${{car.year}}</p>
        <p><strong>Пробег:</strong> ${{car.mileage}}</p>
        <p class="price"><strong>${{car.price.toLocaleString()}} ₽</strong></p>
      </div>
    `;
    const img = new Image();
    img.src = car.image;
    img.onload = () => {{
      card.querySelector('.car-image').style.backgroundImage = `url('${{car.image}}')`;
      card.querySelector('.loader').style.display = 'none';
  }};
    container.appendChild(card);
}});

  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";
  if (totalPages > 1) {{
    for (let i = 1; i <= totalPages; i++) {{
      const link = document.createElement("a");
      link.href = "#";
      link.innerText = i;
      link.className = i === currentPage ? "active" : "";
      link.onclick = function(e) {{
        e.preventDefault();
        currentPage = i;
        renderCatalog();
    }};
      pagination.appendChild(link);
    }}
  }}
}}


renderCatalog();
</script>

<style>
body {{
  margin: 0;
  background: #292929;
  font-family: 'Segoe UI', sans-serif;
  color: white;
}}

.catalog-container {{
  display: flex;
  flex-grow: 1;
  align-items: flex-start;
}}

.sidebar {{
  width: 220px;
  background: #1f1f1f;
  padding: 20px;
  border-radius: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 60vh;
}}

.sidebar h3 {{
  text-align: center;
  font-size: 16px;
  margin: 0;
  padding: 0;
  color: #fff;
  font-weight: bold;
}}

.catalog-title {{
  text-align: center;
  font-size: 36px;
  color: white;
  margin: 40px 0 20px;
  font-weight: bold;
}}

.catalog-wrapper {{
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}}

.brand-list {{
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

.brand-list li {{
  padding: 6px 12px;
  background: #333;
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  color: white;
  text-align: center;
  white-space: nowrap;
}}

.brand-list li:hover,
.brand-list li.active {{
  background: #f70000;
  color: white;
}}

.main-content {{
  flex-grow: 1;
  padding: 20px;
}}

.car-container {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}}

.car-card {{
  opacity: 0;
  animation: fadeInUp 0.5s ease forwards;
  background: #1f1f1f;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  transition: transform 0.3s ease;
}}

.car-card:hover {{
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(255, 0, 0, 0.4);
}}

.car-image {{
  width: 100%;
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
}}

.loader {{
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top: 4px solid white;
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

.car-info {{
  padding: 16px;
}}

.car-info h3 {{
  margin: 0 0 10px;
  font-size: 17px;
  color: #fff;
}}

.car-info p {{
  margin: 4px 0;
  font-size: 14px;
  color: #ccc;
}}

.car-info .price {{
  color: #f70000;
  font-weight: bold;
  font-size: 16px;
  margin-top: 10px;
}}

.pagination {{
  margin-top: 30px;
  text-align: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}}

.pagination a {{
  background: #1f1f1f;
  color: white;
  padding: 8px 14px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  font-size: 14px;
  min-width: 36px;
  text-align: center;
}}

.pagination a.active {{
  background: #f70000;
  color: #fff;
}}

.popup-overlay {{
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}}

.popup-content {{
  background: #fff;
  color: #000;
  padding: 20px;
  border-radius: 15px;
  width: 90%;
  max-width: 400px;
  position: relative;
}}

.popup-close {{
  position: absolute;
  top: 10px; right: 15px;
  font-size: 24px;
  cursor: pointer;
}}

.popup-image {{
  width: 100%;
  height: 180px;
  background-size: cover;
  background-position: center;
  border-radius: 12px;
  margin-bottom: 16px;
}}

#order-form input {{
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

#order-form input:focus {{
  outline: none;
  border-color: #f70000;
}}

#order-form input:-webkit-autofill {{
  box-shadow: 0 0 0 1000px white inset !important;
  -webkit-text-fill-color: black !important;
}}

#order-form button {{
  width: 100%;
  background-color: #f70000 !important;
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

#order-form button:hover {{
  background-color: #d60000 !important;
}}

@media (max-width: 768px) {{
  .catalog-container {{
    flex-direction: column;
  }}

  .sidebar {{
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

  .sidebar h3 {{
    display: none;
  }}

  .brand-list {{
    flex-direction: row;
    max-height: none;
    padding: 0 10px;
  }}

  .brand-list li {{
    flex-shrink: 0;
    font-size: 13px;
    scroll-snap-align: start;
  }}

  .car-container {{
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }}

  .car-card {{
    font-size: 12px;
    border-radius: 10px;
  }}

  .car-image {{
    height: 120px;
  }}

  .car-info h3 {{
    font-size: 14px;
  }}

  .car-info p {{
    font-size: 12px;
  }}

  .car-info .price {{
    font-size: 14px;
  }}
}}
</style>

<!-- END: Sidebar Car Catalog -->
'''

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html_block)

print(f"✅ HTML saved to '{OUTPUT_FILE}'")
