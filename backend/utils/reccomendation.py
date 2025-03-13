import openai
import logging
from database import get_frequent_parts, get_user_search_history
"""Модуль, который возвращает ответ от ИИ.
    Для работы нужно вставить токен в текстовый файл."""
def load_openai_token(filename="openai_token.txt"):
    try:
        with open(filename, "r") as file:
            return file.read().strip()  # Читаем токен и убираем лишние пробелы/переносы строк
    except FileNotFoundError:
        raise ValueError("Файл с API-ключом не найден!")
    except Exception as e:
        raise ValueError(f"Ошибка при чтении API-ключа: {e}")

# Загружаем токен
openai.api_key = load_openai_token()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler("recommendation.log"), logging.StreamHandler()]
    )

def analyze_popular_parts(limit=10):
    try:
        parts = get_frequent_parts(limit)
        if not parts:
            logging.warning("Нет данных о популярных запчастях.")
            return "Нет данных для анализа."

        prompt = f"Какие из этих запчастей могут стать дефицитом или подорожать: {parts}?"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        result = response["choices"][0]["message"]["content"]
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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        result = response["choices"][0]["message"]["content"]
        logging.info("Рекомендации для пользователя %s: %s", user_id, result)
        return result
    except Exception as e:
        logging.error("Ошибка при генерации рекомендаций для пользователя %s: %s", user_id, e)
        return "Ошибка при анализе."

if __name__ == "__main__":
    setup_logging()
    logging.info("Запуск анализа запчастей...")
    print(analyze_popular_parts())
