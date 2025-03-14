import openai
import logging
import sys
import os
from key import api_key


# Add the parent directory to the Python path (if you need it for database.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Now you can import from database.py (if you need it)
# from database import get_frequent_parts, get_user_search_history

# Initialize the OpenAI client
client = openai.OpenAI(api_key=api_key) # Replace with your actual API key or load it from a file

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler("recommendation.log"), logging.StreamHandler()]
    )

def test(text):
    try:
        prompt = f"""Ты API, предоставляющий данные о характеристиках автомобиля по VIN. 

На вход тебе передаётся VIN, а ты должен вернуть JSON-ответ с данными, соответствующими следующей модели:

{{
    "vin_id": "1HGCM82633A123456",
    "model_year_from_vin": "2003",
    "model_year": "2003",
    "made_in": "Japan",
    "model_detail": "Accord EX-L",
    "epc": "XYZ123",
    "epc_id": "45678",
    "brand": "Honda",
    "factory": "Suzuka",
    "series": "Accord",
    "model": "EX-L",
    "sales_version": "North America",
    "capacity": "2.4L",
    "engine_no": "K24A4",
    "kilowatt": "118",
    "horse_power": "160",
    "air_intake": "Natural Aspiration",
    "fuel_type": "Gasoline",
    "transmission_detail": "5-Speed Automatic",
    "gear_num": "5",
    "driving_mode": "FWD",
    "door_num": "4",
    "seat_num": "5",
    "body_type": "Sedan",
    "price": "25000",
    "price_unit": "USD"
}}

Правила генерации:  
- Все данные должны быть реалистичными и соответствовать указанному VIN.  
- Поля **vin_id**, **model_year_from_vin**, **model**, **brand** и **fuel_type** обязательны.  
- Если данные по какому-то полю отсутствуют, оно должно содержать `null`.  
- Возвращай **только JSON** без дополнительных пояснений.  
vin: {text}
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        result = response.choices[0].message.content
        return result
    except Exception as e:
        logging.error(f"Error in test function: {e}")
        return f"Error: {e}"

def analyze_popular_parts(limit=10):
    try:
        parts = get_frequent_parts(limit)
        if not parts:
            logging.warning("Нет данных о популярных запчастях.")
            return "Нет данных для анализа."
        prompt = f"Какие из этих запчастей могут стать дефицитом или подорожать: {parts}?"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        result = response.choices[0].message.content
        logging.info("Результат анализа популярных запчастей: %s", result)
        return result
    except Exception as e:
        logging.error("Ошибка при анализе популярных запчастей: %s", e)
        return "Ошибка при анализе."

def recommend_for_user(user_id):
    try:
        search_history = get_user_search_history(user_id)
        if not search_history:
            logging.warning("Нет данных о поиске пользователя %s.", user_id)
            return "Нет данных для рекомендаций."

        prompt = f"Какие запчасти можно порекомендовать на основе истории поиска: {search_history}?"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        result = response.choices[0].message.content
        logging.info("Рекомендации для пользователя %s: %s", user_id, result)
        return result
    except Exception as e:
        logging.error("Ошибка при генерации рекомендаций для пользователя %s: %s", user_id, e)
        return "Ошибка при анализе."

if __name__ == "__main__":
    setup_logging()
    logging.info("Запуск анализа запчастей...")
    print(test("1FMRU17L7XLB35207"))
    logging.info("анализ закончен")
