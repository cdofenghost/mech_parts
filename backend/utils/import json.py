import requests

url = "https://baza.drom.ru/resources/assets/auto-parts-search-form.91080d4eba4fa1bc31c5.js?1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    js_code = response.text
    print(js_code)
    print("Файл 'search-form.js' успешно скачан!")
else:
    print(f"Ошибка: {response.status_code}")
