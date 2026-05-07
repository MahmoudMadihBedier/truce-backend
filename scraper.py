import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
    }

def scrape_jumia():
    print("Scraping Jumia Egypt...")
    base_url = "https://www.jumia.com.eg"
    categories = ["groceries", "phones-tablets", "electronics", "home-office"]
    results = []

    for cat in categories:
        url = f"{base_url}/{cat}/"
        try:
            res = requests.get(url, headers=get_headers(), timeout=10)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.content, "html.parser")
            products = soup.select("article.prd")[:25]

            for prd in products:
                try:
                    name = prd.select_one("h3.name").text.strip()
                    link = base_url + prd.select_one("a.core")["href"]
                    price_text = prd.select_one("div.prc").text.replace("EGP", "").replace(",", "").strip()
                    price = float(price_text)

                    old_price_tag = prd.select_one("div.old")
                    mrp = price
                    if old_price_tag:
                        mrp = float(old_price_tag.text.replace("EGP", "").replace(",", "").strip())

                    img = prd.select_one("img.img")
                    img_url = img.get("data-src") or img.get("src")

                    raw_id = link.split("-")[-1].replace(".html", "").replace("/", "")
                    try:
                        product_id = int(raw_id)
                    except:
                        product_id = raw_id

                    results.append({
                        "Product URL": link,
                        "Product ID": product_id,
                        "Product Name": name,
                        "Category": f"Home | Supermarket | {cat.capitalize()}",
                        "Brand": name.split()[0],
                        "MRP (EGP)": mrp,
                        "Price": price,
                        "Discount %": round(((mrp - price) / mrp * 100)) if mrp > price else "N/A",
                        "Description": f"{name} available on Jumia Egypt. High quality product with fast delivery in Cairo, Giza and Alexandria.",
                        "Product Image URL": img_url,
                        "Store Name": "Jumia Egypt",
                        "Availability Status": "In Stock",
                        "Location": "Cairo / Alexandria / Giza"
                    })
                except: continue
        except: continue

    return results

def scrape_amazon():
    print("Scraping Amazon Egypt...")
    base_url = "https://www.amazon.eg"
    queries = ["coffee", "electronics", "household"]
    results = []

    for query in queries:
        url = f"{base_url}/s?k={query}"
        try:
            res = requests.get(url, headers=get_headers(), timeout=10)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.content, "html.parser")
            items = soup.select(".s-result-item[data-component-type='s-search-result']")[:20]

            for item in items:
                try:
                    name = item.select_one("h2 span").text.strip()
                    link = base_url + item.select_one("h2 a")["href"]
                    price_whole = item.select_one(".a-price-whole")
                    if not price_whole: continue
                    price = float(price_whole.text.replace(",", "").strip())

                    img_url = item.select_one(".s-image")["src"]

                    results.append({
                        "Product URL": link,
                        "Product ID": link.split("/dp/")[1].split("/")[0] if "/dp/" in link else "AMZ-" + str(random.randint(1000,9999)),
                        "Product Name": name,
                        "Category": f"Home | Amazon | {query.capitalize()}",
                        "Brand": name.split()[0],
                        "MRP (EGP)": price,
                        "Price": price,
                        "Discount %": "N/A",
                        "Description": f"{name} on Amazon Egypt. Reliable pricing and coverage for all Egyptian governorates.",
                        "Product Image URL": img_url,
                        "Store Name": "Amazon Egypt",
                        "Availability Status": "In Stock",
                        "Location": "Nationwide"
                    })
                except: continue
        except: continue

    return results

def scrape_noon_sim():
    return [{
        "Product URL": "https://www.noon.com/egypt-en/p-12345",
        "Product ID": 12345,
        "Product Name": "Noon Premium Product",
        "Category": "Home | Supermarket",
        "Brand": "Noon",
        "MRP (EGP)": 500,
        "Price": 450,
        "Discount %": 10,
        "Description": "Premium product from Noon Egypt. Best price guaranteed.",
        "Product Image URL": "https://z.nooncdn.com/products/tr:n-t_240/v1605814144/N41247601A_1.jpg",
        "Store Name": "Noon Egypt",
        "Availability Status": "In Stock",
        "Location": "Online"
    }]

def scrape_carrefour_sim():
    return [{
        "Product URL": "https://www.carrefouregypt.com/mafegy/en/p/99999",
        "Product ID": 99999,
        "Product Name": "Carrefour Fresh Item",
        "Category": "Home | Fresh Food",
        "Brand": "Carrefour",
        "MRP (EGP)": 100,
        "Price": 90,
        "Discount %": 10,
        "Description": "Fresh item from Carrefour Egypt. Available for same day delivery.",
        "Product Image URL": "https://cdn.mafrservices.com/pim-content/EGY/media/product/99999/main.jpg",
        "Store Name": "Carrefour Egypt",
        "Availability Status": "In Stock",
        "Location": "Cairo / Giza"
    }]

def run_full_scraper():
    all_products = []
    all_products.extend(scrape_jumia())
    all_products.extend(scrape_amazon())
    all_products.extend(scrape_noon_sim())
    all_products.extend(scrape_carrefour_sim())

    # Randomize to ensure mix of stores in default view
    random.shuffle(all_products)

    # Re-assign Sr No
    for i, p in enumerate(all_products):
        p["Sr No"] = i + 1

    output_path = "products_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    print(f"Sync complete. Total: {len(all_products)}")

if __name__ == "__main__":
    run_full_scraper()
