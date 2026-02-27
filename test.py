""" Парсер для сайта dim.ria """

import cloudscraper 
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lxml

base_url = "https://dom.ria.com/uk/arenda-kvartir/?page=1"

def get_listing_urls(base_url):
    """ 
    Завантаження сторінки і 
    витягання всіх посилань на оголошення
    """

    scraper = cloudscraper.create_scraper()
    response = scraper.get(base_url)
    soup = BeautifulSoup(response.text, "lxml")
    links = soup.select("section.realty-item a.all-clickable")

    urls = []

    for link in links:
        href = link.get("href")
        full_url = "https://dom.ria.com" + href
        urls.append(full_url)

    print(f"Знайдено {len(urls)} оголошень")
    return urls

def get_info(driver, url):
    """ 
    Відкриває сторінку Chrome і 
    дістає інформацію
    """

    driver.get(url)
    
    try:
        price_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".price b.size30"))
        )
        price = price_el.text.strip()
    except Exception:
        price = "не знайдено"

    return price

#     def safe_find(selector):
# #       щоб не падав якщо якийсь елемент відсутній на сторінці
#         try:
#             return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
#         except:
#             return "не знайдено"

#     return {
#         "price":    safe_find(".price b.size30"),
#         "address":  safe_find(".your-address-selector"),
#         "rooms":    safe_find(".your-rooms-selector"),
#         "area":     safe_find(".your-area-selector"),
#         # ... скільки треба
#     }


def main():
#   Збираємо посилання з сторінки
    urls = get_listing_urls(base_url)
    if not urls:
        print("Посилання не знайдено — перевір селектор у get_listing_urls()")
        return
    
#   Запускаємо браузер і збираємо дані з кожної сторінки 
    driver = uc.Chrome(version_main=144, headless=False)
    results = []

    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] {url}")
        price = get_info(driver, url)
        print(f"  Ціна: {price}")
        results.append({
            "url": url,
            "price": price,
        })
        time.sleep(random.uniform(3, 5))

    driver.quit()
    
#   Зберігаємо зібрані дані в .csv
    df = pd.DataFrame(results)
    df.to_csv("data/raw/result_2.csv", index=False, encoding="utf-8-sig")
    print(f"\nГотово! Збережено {len(df)} записів у results.csv")
    print(df)

if __name__ == "__main__":
    main()
