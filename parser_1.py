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

base_url = "https://dom.ria.com/uk/arenda-kvartir/?page={page}"
max_pages = 250

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
    
    def safe_find_city(selector, by=By.CSS_SELECTOR):
        try:
            return driver.find_element(by, selector).text.strip()
        except:
            return "не знайдено"

    def get_full_description(selector):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)

            texts =[]
            for el in elements:
                raw_text = el.get_attribute("textContent")
                clean_text  = " ".join(raw_text.split())

                if clean_text:
                    texts.append(clean_text)

            if texts:
                return "| ".join(texts)
            else:
                return "не знайдено"
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
        "technically_tested": safe_find_all("div.inspected-box div"),
        "seller_name": safe_find_all("div.sellerBox div.ml-10"),
        "seller_trust": safe_find("div.sellerBox div.ml-30"),
        "city": safe_find_city("//ul[contains(@class, 'realty-info')]/preceding-sibling::span[1]", By.XPATH),
        "plus_text": get_full_description("#additionalInfo li")
    }
    
def main():
#   Збираємо посилання з сторінки
    
    
#   Запускаємо браузер і збираємо дані з кожної сторінки 
    driver = uc.Chrome(version_main=145, headless=False)
    results = []
    current_page = 1

    try:
        for page in range(1, max_pages + 1):
            current_page = page
            page_url = base_url.format(page=page)
            print(f"\n=== Сторінка {page} ===")

            urls = get_listing_urls(page_url)
            if not urls:
                print("Сторінка {page} порожня")
                break

            for i, url in enumerate(urls):
                print(f"Сторінка: {page} ")
                print(f"[{i+1}/{len(urls)}] {url}")
                info = get_info(driver, url)
                info['url'] = url
                info['page'] = page
                print(f"  Ціна: {info['price_UAH']}")
                print(f"  Заголовок: {info['title']}")
                results.append(info)
                time.sleep(random.uniform(3, 5))

            time.sleep(random.uniform(2,4))
            
    except KeyboardInterrupt:
        print(f"\nЗупинено вручну на сторінці {current_page}")

    except Exception as e:
        print(f"\nПомилка на сторінці: {current_page}: {e}")

    finally:
        driver.quit()

    #   Зберігаємо зібрані дані в .csv
        if results:
            df = pd.DataFrame(results)
            df.to_csv("data/raw/result_test_5000.csv", index=False, encoding="utf-8-sig")
            print(f"\nГотово! Збережено {len(df)} записів у results.csv")
            print(df)
        else:
            print("Даних немає - нічого зберігати")

if __name__ == "__main__":
    main()
