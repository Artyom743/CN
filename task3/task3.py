import time
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


driver = webdriver.Chrome()
driver.get("https://market.yandex.ru/")

search_box = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Найти товары']"))
)

product = input("Какой товар интересует?")

search_box.send_keys(product)
time.sleep(2)

search_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
)
search_button.click()

time.sleep(5)

max_pages = int(input("Сколько страниц спарсить? (например, 3): "))

all_products = [['Title','Price', 'Rate', 'Delivery-wrapper']]
current_page = 1

while current_page <= max_pages:
    print(current_page)
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
        
        product = [title, price, rate, delivery]

        all_products.append(product)

    current_page+=1

    next_button = driver.find_element(By.CSS_SELECTOR, "[data-auto='pagination-next']")

with open('yandex.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(all_products)
    

