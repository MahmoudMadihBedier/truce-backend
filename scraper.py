import os
import time
import random
import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def scrape_jumia_live(query):
    print(f"[*] Live Scrape Jumia: {query}")
    url = f"https://www.jumia.com.eg/catalog/?q={query}"
    results = []
    try:
        res = requests.get(url, headers=get_headers(), timeout=5)
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
                    "Category": "General",
                    "Brand": name.split()[0],
                    "Location": "Online",
                    "Availability Status": "In Stock"
                })
            except: continue
        return results
    except: return []

def scrape_amazon_live(query):
    print(f"[*] Live Scrape Amazon: {query}")
    url = f"https://www.amazon.eg/s?k={query}"
    results = []
    try:
        res = requests.get(url, headers=get_headers(), timeout=5)
        if res.status_code != 200: return []
        soup = BeautifulSoup(res.content, "html.parser")
        for i, item in enumerate(soup.select(".s-result-item[data-component-type='s-search-result']")[:6]):
            try:
                name = item.select_one("h2 span").text.strip()
                link = "https://www.amazon.eg" + item.select_one("h2 a")["href"]
                price_tag = item.select_one(".a-price-whole")
                if not price_tag: continue
                price = float(price_tag.text.replace(",", "").strip())
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
                    "Category": "General",
                    "Brand": name.split()[0],
                    "Location": "Online",
                    "Availability Status": "In Stock"
                })
            except: continue
        return results
    except: return []
