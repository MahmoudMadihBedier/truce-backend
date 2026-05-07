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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def sync_to_db(items, store_id):
    """
    Clears old data for the store and saves new data to Supabase.
    """
    try:
        if not items:
            return

        # 1. Mark existing prices for this store as unavailable or older
        # Note: In a real scenario, we might want to delete them if they are very old.
        # supabase.table("product_prices").delete().eq("store_id", store_id).execute()

        for item in items:
            # 2. Upsert product
            product_data = {
                "name_en": item["Product Name"],
                "category_id": 3, # Default
                "image_url": item["Product Image URL"],
                "source_url": item["Product URL"],
                "brand": item.get("Brand", "N/A"),
                "description_en": item.get("Description", "")
            }

            prod_res = supabase.table("products").upsert(product_data, on_conflict="name_en").execute()
            if prod_res.data:
                product_id = prod_res.data[0]["id"]
                # 3. Upsert price
                price_data = {
                    "product_id": product_id,
                    "store_id": store_id,
                    "price": item["Price"],
                    "mrp": item["MRP (EGP)"],
                    "product_url": item["Product URL"],
                    "is_available": True,
                    "updated_at": "now()"
                }
                supabase.table("product_prices").upsert(price_data, on_conflict="product_id,store_id").execute()
    except Exception as e:
        print(f"Database sync error: {e}")

def scrape_jumia_live(query):
    print(f"[*] Live Scrape Jumia: {query}")
    url = f"https://www.jumia.com.eg/catalog/?q={query}"
    results = []
    try:
        res = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        for i, prd in enumerate(soup.select("article.prd")[:10]):
            try:
                name = prd.select_one("h3.name").text.strip()
                link = "https://www.jumia.com.eg" + prd.select_one("a.core")["href"]
                price_text = prd.select_one("div.prc").text.replace("EGP", "").replace(",", "").strip()
                price = float(price_text)
                mrp = None
                if prd.select_one("div.old"):
                    mrp = float(prd.select_one("div.old").text.replace("EGP", "").replace(",", "").strip())
                img = prd.select_one("img.img")["data-src"]

                results.append({
                    "Sr No": i + 1,
                    "Product URL": link,
                    "Product Name": name,
                    "Price": price,
                    "MRP (EGP)": mrp or price,
                    "Discount %": round(((mrp - price) / mrp * 100)) if mrp and mrp > price else "N/A",
                    "Product Image URL": img,
                    "Store Name": "Jumia",
                    "Description": f"{name} available on Jumia Egypt",
                    "Category": "Supermarket",
                    "Brand": name.split()[0],
                    "Location": "Online",
                    "Availability Status": "In Stock"
                })
            except: continue

        sync_to_db(results, 5) # Jumia Store ID
        return results
    except Exception as e:
        print(f"Jumia Live Error: {e}")
        return []

def scrape_amazon_live(query):
    print(f"[*] Live Scrape Amazon: {query}")
    url = f"https://www.amazon.eg/s?k={query}"
    results = []
    try:
        res = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        for i, item in enumerate(soup.select(".s-result-item[data-component-type='s-search-result']")[:10]):
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

        sync_to_db(results, 1) # Amazon Store ID
        return results
    except Exception as e:
        print(f"Amazon Live Error: {e}")
        return []

if __name__ == "__main__":
    print(scrape_jumia_live("coffee")[:1])
