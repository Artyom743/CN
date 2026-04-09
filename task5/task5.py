import os
import time

from fastapi import FastAPI, Query, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Gffgtfgfcnjdr')
DB_URL = f"postgresql://postgres:{DB_PASSWORD}@{DB_HOST}:5432/market_parser"

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(String)
    rate = Column(String)
    delivery = Column(Text)

Base.metadata.create_all(bind=engine)

def parse_yandex():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    all_products = []
    
    try:
        print("Переходим на market.yandex.ru...")
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.get("https://market.yandex.ru/")
        time.sleep(5)
        
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
        search_box.send_keys("Подарок")
        search_box.submit()
        time.sleep(5)
        
        max_pages = 3
        current_page = 1
        
        while current_page <= max_pages:
            print(f"Парсинг страницы {current_page}...")
            
            time.sleep(5)
            
            snippets = driver.find_elements(By.CSS_SELECTOR, "[data-baobab-name='productSnippet']")
            print(f"Найдено товаров на странице: {len(snippets)}")
            
            for snippet in snippets:
                try:
                    try:
                        title_elem = snippet.find_element(By.CSS_SELECTOR, "[data-zone-name='title']")
                        title = title_elem.text
                    except:
                        title = "Нет названия"
                    
                    try:
                        delivery_info = snippet.find_element(By.CSS_SELECTOR, "[data-zone-name='deliveryInfo']")
                        delivery = delivery_info.find_element(By.CSS_SELECTOR, "span[class*='ds-text']")
                        delivery = delivery.text
                        delivery = delivery.replace('\u2009', ' ').replace('\u202f', ' ')
                        delivery = ' '.join(delivery.split())
                    except:
                        delivery = "Нет информации о доставке"
                    
                    try:
                        price_info = snippet.find_element(By.CSS_SELECTOR, "[data-auto='snippet-price-current']")
                        price = price_info.text.replace('\u2006', '').replace('\n', ' ')
                    except:
                        price = "Нет цены"
                    
                    try:
                        rate_elem = snippet.find_element(By.CSS_SELECTOR, "[data-zone-name='rating']")
                        rate = rate_elem.find_element(By.CSS_SELECTOR, "span.ds-visuallyHidden")
                        rate = rate.text
                    except:
                        rate = "Нет рейтинга"
                    
                    all_products.append({
                        'title': title,
                        'price': price,
                        'rate': rate,
                        'delivery': delivery
                    })
                except Exception as e:
                    print(f"Ошибка при парсинге товара: {e}")
                    continue
            
            current_page += 1
            if current_page <= max_pages:
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-auto='pagination-next']"))
                    )
                    next_button.click()
                    print("Переход на следующую страницу")
                    time.sleep(5)
                except Exception as e:
                    print(f"Не удалось перейти на следующую страницу: {e}")
                    break
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
    
    return all_products

app = FastAPI()

def check_url(url):
    if 'market.yandex.ru' not in url:
        raise HTTPException(status_code=400, detail="Нет. Тока Яндекс Маркет. Тока market.yandex.ru")

@app.get("/parse")
def parse_url(url):
    check_url(url)
    products = parse_yandex()
    
    db = Session()
    for p in products:
        db.add(Product(**p))
    db.commit()
    db.close()
    
    return {"saved": len(products)}

@app.get("/data")
def get_data():
    db = Session()
    products = db.query(Product).all()
    db.close()
    return [{"id": p.id, "title": p.title, "price": p.price, "rate": p.rate, "delivery": p.delivery} for p in products]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)