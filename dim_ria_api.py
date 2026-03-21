import requests
import json

# API_KEY = 

# Пробуємо отримати характеристики для квартир (1-Нерухомість, 2-Квартира, 3-Довгострокова оренда)
url = f"https://developers.ria.com/dom/options?category=1&realty_type=2&operation_type=3&api_key={API_KEY}"

print("Завантажуємо довідник характеристик...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # Зберігаємо результат у файл, щоб зручно було шукати очима
    filename = "dom_ria_options.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        
    print(f"Успішно! Усі параметри збережено у файл {filename}.")
else:
    print(f"Помилка {response.status_code}: {response.text}")