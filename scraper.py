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

_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def sync_to_db(items, store_id):
    try:
        if not items: return
        sb = get_supabase()
        for item in items[:5]: # Only sync top 5 to save time in serverless
            product_data = {
                "name_en": item["Product Name"],
                "category_id": 3,
                "image_url": item["Product Image URL"],
                "source_url": item["Product URL"],
                "brand": item.get("Brand", "N/A"),
                "description_en": item.get("Description", "")
            }
            prod_res = sb.table("products").upsert(product_data, on_conflict="name_en").execute()
            if prod_res.data:
                product_id = prod_res.data[0]["id"]
                price_data = {
                    "product_id": product_id,
                    "store_id": store_id,
                    "price": item["Price"],
                    "mrp": item["MRP (EGP)"],
                    "product_url": item["Product URL"],
                    "is_available": True,
                    "updated_at": "now()"
                }
                sb.table("product_prices").upsert(price_data, on_conflict="product_id,store_id").execute()
    except Exception as e:
        print(f"Sync error: {e}")

def scrape_jumia_live(query):
    url = f"https://www.jumia.com.eg/catalog/?q={query}"
    results = []
    try:
        res = requests.get(url, headers=get_headers(), timeout=7)
        if res.status_code != 200: return []
        soup = BeautifulSoup(res.content, "html.parser")
        for i, prd in enumerate(soup.select("article.prd")[:6]):
            try:
                name = prd.select_one("h3.name").text.strip()
                link = "https://www.jumia.com.eg" + prd.select_one("a.core")["href"]
                price_text = prd.select_one("div.prc").text.replace("EGP", "").replace(",", "").strip()
                price = float(price_text)
                mrp = price
                if prd.select_one("div.old"):
                    mrp = float(prd.select_one("div.old").text.replace("EGP", "").replace(",", "").strip())
                img = prd.select_one("img.img").get("data-src") or prd.select_one("img.img").get("src")

                results.append({
                    "Sr No": i + 1,
                    "Product URL": link,
                    "Product Name": name,
                    "Price": price,
                    "MRP (EGP)": mrp,
                    "Discount %": round(((mrp - price) / mrp * 100)) if mrp > price else "N/A",
                    "Product Image URL": img,
                    "Store Name": "Jumia",
                    "Description": f"{name} available on Jumia Egypt",
                    "Category": "Supermarket",
                    "Brand": name.split()[0],
                    "Location": "Online",
                    "Availability Status": "In Stock"
                })
            except: continue
        sync_to_db(results, 5)
        return results
    except: return []

def scrape_amazon_live(query):
    url = f"https://www.amazon.eg/s?k={query}"
    results = []
    try:
        res = requests.get(url, headers=get_headers(), timeout=7)
        if res.status_code != 200: return []
        soup = BeautifulSoup(res.content, "html.parser")
        for i, item in enumerate(soup.select(".s-result-item[data-component-type='s-search-result']")[:6]):
            try:
                name = item.select_one("h2 span").text.strip()
                link = "https://www.amazon.eg" + item.select_one("h2 a")["href"]
                price_whole = item.select_one(".a-price-whole").text.replace(",", "").strip()
                price = float(price_whole)
                img = item.select_one(".s-image")["src"]
                results.append({
                    "Sr No": i + 1,
                    "Product URL": link,
                    "Product Name": name,
                    "Price": price,
                    "MRP (EGP)": price,
                    "Discount %": "N/A",
                    "Product Image URL": img,
                    "Store Name": "Amazon",
                    "Description": f"{name} available on Amazon Egypt",
                    "Category": "N/A",
                    "Brand": name.split()[0],
                    "Location": "Online",
                    "Availability Status": "In Stock"
                })
            except: continue
        sync_to_db(results, 1)
        return results
    except: return []
