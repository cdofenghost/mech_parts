from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

BASE_PRICE_URL = "https://baza.drom.ru/oem"

def get_prices(part_number: str) -> list[float]:
    """Получает список цен для запчасти с указанным OEM-номером, дожидаясь загрузки страницы."""

    url = f"{BASE_PRICE_URL}/{part_number}/"

    # Настройки для браузера
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Фоновый режим без UI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service()  # Использует системный ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # Ждём, пока появятся элементы с ценами (до 10 секунд)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "price-block__price"))
        )

        # Собираем все найденные элементы с ценами
        price_elements = driver.find_elements(By.CLASS_NAME, "price-block__price")

        price_list = []
        for price_element in price_elements:
            price_text = price_element.text.strip().replace(" ", "").replace("₽", "")
            try:
                price_list.append(float(price_text))
            except ValueError:
                continue

        if not price_list:
            raise Exception("Не удалось найти цены на странице")

        return price_list

    finally:
        driver.quit()

def get_average_price(part_number: str) -> float:
    """Возвращает среднюю цену детали."""
    try:
        prices = get_prices(part_number)
        print(f"{(sum(prices) / len(prices)):.2f}")
        return f"{(sum(prices) / len(prices)):.2f}" if prices else 0
    except Exception as e:
        print(f"Ошибка: {e}")
        return 0

