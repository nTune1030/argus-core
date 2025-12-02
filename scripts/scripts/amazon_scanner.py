#!/usr/bin/env python3
import sys
import re
import csv
import os
import random
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
# Example: Sony WH-1000XM5 Headphones
AMAZON_URL = "https://www.amazon.com/dp/B09XS7JWHH" 
TARGET_PRICE = 350.00
ITEM_NAME = "Sony WH-1000XM5"

CSV_PATH = "/home/ntune1030/nas_storage/amazon_prices.csv"
DEBUG_HTML_PATH = "/home/ntune1030/nas_storage/amazon_debug.html"
DEBUG_IMG_PATH = "/home/ntune1030/nas_storage/amazon_debug.png"

def parse_price(text):
    if not text: return None
    try:
        clean = re.sub(r'[^\d.]', '', text)
        return float(clean)
    except:
        return None

def save_to_csv(price, title):
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Item', 'Price', 'Link'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, price, AMAZON_URL])

def check_amazon():
    # We DO NOT print "Checking..." here because Orchestrator logs are only emailed if not empty.
    # We want silence if no deal is found.
    
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        )
        page = context.new_page()

        try:
            page.goto(AMAZON_URL, timeout=60000)
            time.sleep(random.uniform(3, 6))
            
            # Only take screenshot if we actually fail or find a deal (saves CPU)
            # page.screenshot(path=DEBUG_IMG_PATH) 

            price_selectors = [
                '.a-price .a-offscreen',
                '#priceblock_ourprice',
                '#priceblock_dealprice',
                '.a-price-whole',
                '#corePriceDisplay_desktop_feature_div .a-offscreen'
            ]
            
            price_text = None
            for selector in price_selectors:
                if page.locator(selector).count() > 0:
                    price_text = page.locator(selector).first.inner_text()
                    # print(f"   -> Found price using selector: {selector}") # Silenced
                    break
            
            title_text = "Unknown Item"
            if page.locator("#productTitle").count() > 0:
                title_text = page.locator("#productTitle").first.inner_text().strip()

            if price_text:
                price = parse_price(price_text)
                # print(f"   -> Current Price: ${price}") # Silenced
                
                save_to_csv(price, title_text)

                if price and price < TARGET_PRICE:
                    # THIS IS THE ONLY PRINT THAT SHOULD HAPPEN ON SUCCESS
                    print(f"🔥 AMAZON DEAL: {ITEM_NAME}")
                    print(f"   Price: ${price}")
                    print(f"   Link: {AMAZON_URL}\n")
                    
                    # Take proof photo only now
                    page.screenshot(path=DEBUG_IMG_PATH)
                    print(f"   (Screenshot saved to Z:/amazon_debug.png)")
            else:
                # This is an error state, so we print it to trigger an email report
                print("❌ ERROR: Could not find Amazon price.")
                page.screenshot(path=DEBUG_IMG_PATH)
                print("   (Debug screenshot taken)")
                
                with open(DEBUG_HTML_PATH, "w", encoding="utf-8") as f:
                    f.write(page.content())

        except Exception as e:
            print(f"❌ CRITICAL ERROR: {e}")
            page.screenshot(path=DEBUG_IMG_PATH)
        
        browser.close()

if __name__ == "__main__":
    check_amazon()