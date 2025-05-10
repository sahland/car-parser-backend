import requests

def get_cny_to_rub_rate():
    try:
        url = "https://api.exchangerate.host/latest?base=CNY&symbols=RUB"
        response = requests.get(url, timeout=5)
        data = response.json()
        return round(data["rates"]["RUB"], 2)
    except Exception as e:
        print(f"❌ Не удалось получить курс: {e}")
        return 12  # fallback по умолчанию