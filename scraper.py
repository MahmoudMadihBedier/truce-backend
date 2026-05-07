import os
import time
import random
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# SUPABASE CONFIG
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mgqcolwglaavwazjwjir.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_52t3OZTL4k39wQf8DfrH_g_X7n73_vE")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# USER AGENTS
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def upsert_data(product_data, price_data):
    try:
        # Upsert product
        prod_res = supabase.table("products").upsert(product_data, on_conflict="name_en").execute()
        if prod_res.data:
            price_data["product_id"] = prod_res.data[0]["id"]
            # Upsert price
            supabase.table("product_prices").upsert(price_data, on_conflict="product_id,store_id").execute()
            print(f"  [+] Saved: {product_data['name_en'][:40]}... at {price_data['price']} EGP")
    except Exception as e:
        print(f"  [!] Database error: {e}")

# 1. JUMIA EGYPT
def scrape_jumia(category_path, category_id):
    print(f"[*] Scraping Jumia: {category_path}")
    url = f"https://www.jumia.com.eg/{category_path}/"
    try:
        res = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        for prd in soup.select("article.prd")[:15]: # Limit per category
            try:
                name = prd.select_one("h3.name").text.strip()
                link = "https://www.jumia.com.eg" + prd.select_one("a.core")["href"]
                price = float(prd.select_one("div.prc").text.replace("EGP", "").replace(",", "").strip())
                mrp = None
                if prd.select_one("div.old"):
                    mrp = float(prd.select_one("div.old").text.replace("EGP", "").replace(",", "").strip())
                img = prd.select_one("img.img")["data-src"]

                upsert_data(
                    {"name_en": name, "category_id": category_id, "image_url": img, "source_url": link},
                    {"store_id": 5, "price": price, "mrp": mrp, "product_url": link, "is_available": True}
                )
            except: continue
    except Exception as e: print(f"  [!] Jumia Error: {e}")

# 2. AMAZON EGYPT
def scrape_amazon(search_query, category_id):
    print(f"[*] Scraping Amazon Egypt: {search_query}")
    url = f"https://www.amazon.eg/s?k={search_query}"
    try:
        res = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        for item in soup.select(".s-result-item[data-component-type='s-search-result']")[:10]:
            try:
                name = item.select_one("h2 span").text.strip()
                link = "https://www.amazon.eg" + item.select_one("h2 a")["href"]
                price_whole = item.select_one(".a-price-whole").text.replace(",", "").strip()
                price = float(price_whole)
                img = item.select_one(".s-image")["src"]

                upsert_data(
                    {"name_en": name, "category_id": category_id, "image_url": img, "source_url": link},
                    {"store_id": 1, "price": price, "product_url": link, "is_available": True}
                )
            except: continue
    except Exception as e: print(f"  [!] Amazon Error: {e}")

# 3. NOON EGYPT (Simplified)
def scrape_noon(query, category_id):
    print(f"[*] Scraping Noon Egypt: {query}")
    # Noon uses heavy JS, this is a simplified HTML fallback or API-like approach estimation
    url = f"https://www.noon.com/egypt-en/search/?q={query}"
    try:
        res = requests.get(url, headers=get_headers(), timeout=15)
        # Note: Noon often blocks simple BS4. In production, consider using a proxy or Playwright.
        print("  [i] Noon scraping usually requires Playwright/Puppeteer due to JS rendering.")
    except Exception as e: print(f"  [!] Noon Error: {e}")

# 4. CARREFOUR EGYPT (Simplified)
def scrape_carrefour(query, category_id):
    print(f"[*] Scraping Carrefour Egypt: {query}")
    url = f"https://www.carrefouregypt.com/mafegy/en/s?name={query}"
    try:
        res = requests.get(url, headers=get_headers(), timeout=15)
        print("  [i] Carrefour scraping usually requires Playwright/Puppeteer due to JS rendering.")
    except Exception as e: print(f"  [!] Carrefour Error: {e}")

def run_all_scrapers():
    # Mapping Categories to Search Terms
    # 3: Groceries, 1: Electronics, 2: Home Appliances, 5: Fashion
    tasks = [
        {"store": "jumia", "path": "groceries", "cat": 3},
        {"store": "jumia", "path": "phones-tablets", "cat": 1},
        {"store": "amazon", "query": "coffee", "cat": 3},
        {"store": "amazon", "query": "laptop", "cat": 1},
    ]

    for task in tasks:
        if task["store"] == "jumia":
            scrape_jumia(task["path"], task["cat"])
        elif task["store"] == "amazon":
            scrape_amazon(task["query"], task["cat"])
        time.sleep(random.uniform(2, 5)) # Polite delay

if __name__ == "__main__":
    run_all_scrapers()
