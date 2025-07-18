from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import List, Dict
import os

def fetch_whatsapp_messages(chat_name: str, num_messages: int = 10) -> List[Dict]:
    options = Options()
    options.add_argument("--user-data-dir=./chrome_profile")  # Persist login
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Use webdriver-manager to automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://web.whatsapp.com/")
    print("Please scan the QR code if not already logged in...")
    time.sleep(15)  # Wait for login (increase if needed)

    # Search and click chat
    search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search_box.click()
    search_box.clear()
    search_box.send_keys(chat_name)
    time.sleep(2)
    chat = driver.find_element(By.XPATH, f'//span[@title="{chat_name}"]')
    chat.click()
    time.sleep(2)

    # Get last N messages
    messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')
    results = []
    for msg in messages[-num_messages:]:
        try:
            text = msg.find_element(By.XPATH, './/span[@class="selectable-text copyable-text"]').text
            results.append({"text": text})
        except Exception:
            continue
    driver.quit()
    return results 