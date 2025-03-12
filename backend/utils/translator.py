#Функция перевода значений словаря, возвращает словарь 
from googletrans import Translator

def translate_dict(data: dict, src_lang: str = 'en', dest_lang: str = 'ru') -> dict:
    translator = Translator()
    translated_data = {}

    for key, value in data.items():
        if isinstance(value, str):
            translated_value = translator.translate(value, src=src_lang, dest=dest_lang).text
        elif isinstance(value, dict):
            translated_value = translate_dict(value, src_lang, dest_lang)
        else:
            translated_value = value

        translated_data[key] = translated_value

    return translated_data