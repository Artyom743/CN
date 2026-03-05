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


DB_URL = "postgresql://postgres:Gffgtfgfcnjdr@localhost:5432/market_parser"
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
    driver = webdriver.Chrome()
    all_products = []
    
    driver.get("https://market.yandex.ru/")
    
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Найти товары']"))
    )
    
    search_box.send_keys("Подарок")
    time.sleep(2)
    
    search_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
    )
    search_button.click()
    time.sleep(5)
    
    snippets = driver.find_elements(By.CSS_SELECTOR, "[data-baobab-name='productSnippet']")
    time.sleep(5)
    
    for snippet in snippets:
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
    uvicorn.run(app, host="127.0.0.1", port=8000)