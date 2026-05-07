import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mgqcolwglaavwazjwjir.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_52t3OZTL4k39wQf8DfrH_g_X7n73_vE")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Jumia Egypt URL for testing
JUMIA_BASE_URL = "https://www.jumia.com.eg"

def scrape_jumia_category(category_path, category_id):
    url = f"{JUMIA_BASE_URL}/{category_path}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: Status {response.status_code}")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        products = soup.select("article.prd")

        for prd in products:
            try:
                name = prd.select_one("h3.name").text.strip()
                link = JUMIA_BASE_URL + prd.select_one("a.core")["href"]
                price_text = prd.select_one("div.prc").text.strip()
                # Clean price: "EGP 500" -> 500
                price = float(price_text.replace("EGP", "").replace(",", "").strip())

                old_price_tag = prd.select_one("div.old")
                mrp = None
                if old_price_tag:
                    mrp = float(old_price_tag.text.replace("EGP", "").replace(",", "").strip())

                img_url = prd.select_one("img.img")["data-src"]

                # 1. Upsert product
                product_data = {
                    "name_en": name,
                    "category_id": category_id,
                    "image_url": img_url,
                    "source_url": link,
                    "brand": name.split()[0] # Rough brand estimation
                }

                prod_res = supabase.table("products").upsert(product_data, on_conflict="name_en").execute()
                if prod_res.data:
                    product_id = prod_res.data[0]["id"]

                    # 2. Upsert price for Jumia (store_id = 5 based on your DB)
                    price_data = {
                        "product_id": product_id,
                        "store_id": 5,
                        "price": price,
                        "mrp": mrp,
                        "product_url": link,
                        "is_available": True
                    }
                    supabase.table("product_prices").upsert(price_data, on_conflict="product_id,store_id").execute()
                    print(f"Saved: {name} - {price} EGP")

            except Exception as e:
                print(f"Error parsing product: {e}")

    except Exception as e:
        print(f"Scraper error: {e}")

if __name__ == "__main__":
    # Example: Scrape Grocery Category (category_id 3 in your DB)
    print("Starting Jumia Egypt Scraper...")
    scrape_jumia_category("groceries", 3)
    print("Scraper finished.")
