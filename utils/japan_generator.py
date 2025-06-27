import json

OUTPUT_FILE = "car_listings_japan.html"
JSON_INPUT = "./json_data/japan_catalog/japan_brands_with_models.json"

with open(JSON_INPUT, 'r', encoding='utf-8') as f:
    data = json.load(f)

brands = [b["brand"] for b in data["brands"]]

html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Каталог автомобилей прямиком из Японии</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg: #292929;
            --card-bg: #222;
            --hover-bg: #2a2a2a;
            --text: #fff;
            --subtext: #aaa;
            --accent: #ff3b3f;
            --radius: 12px;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: 'Segoe UI', sans-serif;
            background-color: var(--bg);
            color: var(--text);
        }

        header {
            text-align: center;
            padding: 40px 20px 10px;
        }

        header h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 16px;
        }

        .selector-container {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }

        select {
            padding: 12px 16px;
            font-size: 16px;
            border-radius: var(--radius);
            background: var(--card-bg);
            color: var(--text);
            border: 2px solid var(--accent);
            transition: 0.3s;
        }

        select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 2px rgba(255, 59, 63, 0.5);
        }

        .model-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 24px;
            padding: 0 20px 40px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .model-card {
            background: var(--card-bg);
            border-radius: var(--radius);
            padding: 20px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
            transition: transform 0.2s ease, background-color 0.3s ease;
        }

        .model-card:hover {
            background: var(--hover-bg);
            transform: translateY(-4px);
        }

        .model-header {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 12px;
            color: var(--accent);
        }

        .model-price {
            font-size: 16px;
            color: var(--subtext);
        }

        @media (max-width: 600px) {
            .model-list {
                grid-template-columns: 1fr;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Каталог автомобилей прямиком из Японии</h1>
        <div class="selector-container">
            <select id="brandSelect" onchange="filterModels()" autofocus>
'''

# Список брендов
for brand in brands:
    html += f'                <option value="{brand}">{brand}</option>\n'

html += '''            </select>
        </div>
    </header>
    <main>
        <div id="modelContainer" class="model-list"></div>
    </main>

    <script>
        const carData = ''' + json.dumps(data["brands"], ensure_ascii=False) + ''';

        function formatPrice(price) {
            return price.toLocaleString("ru-RU") + " ₽";
        }

        function filterModels() {
            const selectedBrand = document.getElementById("brandSelect").value;
            const container = document.getElementById("modelContainer");
            container.innerHTML = "";

            const brand = carData.find(b => b.brand === selectedBrand);
            if (!brand || !brand.models.length) {
                container.innerHTML = "<p style='color: var(--subtext); text-align: center;'>Нет доступных моделей</p>";
                return;
            }

            for (const model of brand.models) {
                const card = document.createElement("div");
                card.className = "model-card";
                card.innerHTML = `
                    <div class="model-header">${model.name}</div>
                    <div class="model-price">от ${formatPrice(model.avg_price_rub)}</div>
                `;
                container.appendChild(card);
            }
        }

        window.onload = filterModels;
    </script>
</body>
</html>'''

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

import ace_tools as tools; tools.display_dataframe_to_user(name="✅ HTML-файл с красным UI создан", dataframe=None)
