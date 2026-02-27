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
    time.sleep(3)

    def safe_find(selector):
    #   Дістає тільки по одному тегу
        try:
            return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        except:
            return "не знайдено"
        
    def safe_find_all(selector):
    #   Дістає всю інформацію в указаному тегу
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            texts = []
            for el in elements:
                text = el.text.strip()
                if text:
                    texts.append(text)
            if texts:
                return "| ".join(texts)
            else:
                return "не знайдено"
        except:
            return "не знайдено"

    return {
        "price_UAH":   safe_find(".price b.size30"),
        "price_USD":  safe_find(".price span"),
        "title":    safe_find("h1"),
        "location_list":    safe_find_all("span.i-block.mr-4 a"),
        "details_list":     safe_find_all("li.list-item span"),
        "advantages_list":   safe_find_all("ul.unstyle.utp-wrap li"),
        "description": safe_find("div.boxed.descriptionBlock"),
        "created_at": safe_find("ul.realty-info li"),
        "facilities_list": safe_find_all("div.comfort-list-grid span.comfort-list-text"),
        "technically_tested": safe_find_all("div.inspected-box div")
    }
    
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
        info = get_info(driver, url)
        info['url'] = url
        print(f"  Ціна: {info['price_UAH']}")
        print(f"  Заголовок: {info['title']}")
        results.append(info)
        time.sleep(random.uniform(3, 5))

    driver.quit()

#   Зберігаємо зібрані дані в .csv
    df = pd.DataFrame(results)
    df.to_csv("data/raw/result_2.csv", index=False, encoding="utf-8-sig")
    print(f"\nГотово! Збережено {len(df)} записів у results.csv")
    print(df)

if __name__ == "__main__":
    main()
