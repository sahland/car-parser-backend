from playwright.sync_api import sync_playwright

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("⏳ Открываем сайт и перехватываем запросы...")

        def log_request(request):
            if "api2scsou.che168.com/api/v11/search" in request.url:
                print("🔗 Найден API-запрос:")
                print("URL:", request.url)
                print("HEADERS:", dict(request.headers))

        page.on("request", log_request)

        page.goto("https://m.che168.com/beijing/list/", wait_until="domcontentloaded")
        for _ in range(10):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(1500)

        print("✅ Прокрутка завершена. Проверь консоль на наличие API-запроса.")
        page.wait_for_timeout(10000)
        browser.close()
