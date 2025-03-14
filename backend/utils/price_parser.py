from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_PRICE_URL = "https://baza.drom.ru/oem"

def get_prices(part_number: str) -> list[float]:
    """Быстро получает список цен для запчасти с указанным OEM-номером."""
    
    url = f"{BASE_PRICE_URL}/{part_number}/"

    # Оптимизированные настройки Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Новый headless (быстрее)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  
    chrome_options.page_load_strategy = "none"  # Не ждём полной загрузки

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        
        # Ожидание загрузки хотя бы DOM (ускоряет процесс)
        WebDriverWait(driver, 3).until(lambda d: d.execute_script("return document.readyState") == "interactive")

        # Ждём появления хотя бы одной цены
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "price-block__price"))
        )

        # Получаем цены через JS
        prices = driver.execute_script(r"""
            return Array.from(document.querySelectorAll('.price-block__price'))
                .map(el => el.innerText.replace(/\D/g, ''))  // Убираем всё, кроме цифр
                .filter(text => text.length > 0)  // Убираем пустые значения
                .map(Number);  // Преобразуем в числа
        """)

        if not prices:
            raise Exception("Цены не найдены")

        return prices

    finally:
        driver.quit()

def get_average_price(part_number: str) -> int:
    """Возвращает среднюю цену детали."""
    prices = get_prices(part_number)
    return int(sum(prices) / len(prices) if prices else 0)

if __name__ == "__main__":
    part_number = "51350SAAE01"
    try:
        prices = get_prices(part_number)
        print(f"Цены: {prices}")
        print(f"Средняя цена: {get_average_price(part_number):.2f} ₽")
    except Exception as e:
        print(f"Ошибка: {e}")
