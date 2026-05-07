import os
import random
import asyncio
from typing import List, Optional, Union
from fastapi import FastAPI, Query, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv

# Import our live scrapers
import scraper

load_dotenv()

app = FastAPI(
    title="Truce API",
    description="Backend API with Live Real-time Scraping for the Egyptian Market",
    version="2.0.2"
)

# Constants for Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mgqcolwglaavwazjwjir.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_52t3OZTL4k39wQf8DfrH_g_X7n73_vE")

_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def transform_product_price(item, index: int):
    product = item.get("product") or {}
    category = product.get("category") or {}
    store = item.get("store") or {}

    store_name = store.get("name_en", "N/A")
    mrp_val = item.get("mrp")
    price_val = item.get("price")
    discount_pct = item.get("discount_percent")

    final_price = float(price_val) if price_val is not None else "N/A"
    final_mrp = float(mrp_val) if mrp_val is not None else (final_price if final_price != "N/A" else "N/A")

    if discount_pct is None and isinstance(final_mrp, float) and isinstance(final_price, float) and final_mrp > final_price:
        discount_pct = round(((final_mrp - final_price) / final_mrp) * 100)

    return {
        "Sr No": index + 1,
        "Product URL": item.get("product_url") or product.get("source_url") or "N/A",
        "Product ID": product.get("id", "N/A"),
        "Product Name": product.get("name_en") or "N/A",
        "Category": category.get("name_en") if category else "N/A",
        "Brand": product.get("brand") or "N/A",
        "MRP (EGP)": final_mrp,
        "Discount %": discount_pct if discount_pct is not None else "N/A",
        "Price": final_price,
        "Description": product.get("description_en") or "N/A",
        "Product Image URL": product.get("image_url") or "N/A",
        "Store Name": store_name,
        "Location": store.get("location_name_en") or "N/A",
        "Availability Status": "In Stock" if item.get("is_available") else "Out of Stock"
    }

@app.get("/")
def read_root():
    return {"message": "Truce API v2.0.2 - Live Scraping Active"}

@app.get("/products")
async def get_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    store: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = 0
):
    try:
        # If the user is searching for a specific product, we trigger LIVE SCRAPING
        if search and len(search) > 2:
            print(f"[*] Triggering Live Search for: {search}")
            # Use run_in_executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            jumia_data = await loop.run_in_executor(None, scraper.scrape_jumia_live, search)
            amazon_data = await loop.run_in_executor(None, scraper.scrape_amazon_live, search)

            # Combine and interleave
            combined = []
            max_len = max(len(jumia_data), len(amazon_data))
            for i in range(max_len):
                if i < len(jumia_data): combined.append(jumia_data[i])
                if i < len(amazon_data): combined.append(amazon_data[i])

            # Re-index Sr No
            for i, item in enumerate(combined):
                item["Sr No"] = i + 1 + offset

            return combined[:limit]

        # FALLBACK: Database search for general browsing
        sb = get_supabase()
        query = sb.table("product_prices").select(
            "*, product:products(*, category:categories(*)), store:stores(*)"
        )

        if search: query = query.ilike("product.name_en", f"%{search}%")
        if category: query = query.ilike("product.category.name_en", f"%{category}%")
        if brand: query = query.ilike("product.brand", f"%{brand}%")
        if store: query = query.ilike("store.name_en", f"%{store}%")

        query = query.range(offset, offset + 100) # Fetch more for variety
        response = query.execute()
        data = response.data

        if not data: return []

        # Priority sort and transform
        valid_data = [item for item in data if item.get("product")]
        valid_data.sort(key=lambda x: (x.get("product", {}).get("image_url") is not None), reverse=True)

        result = [transform_product_price(item, i + offset) for i, item in enumerate(valid_data[:limit])]
        return result

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}

@app.get("/categories")
async def get_categories():
    sb = get_supabase()
    res = sb.table("categories").select("*").execute()
    return res.data

@app.get("/stores")
async def get_stores():
    sb = get_supabase()
    res = sb.table("stores").select("*").execute()
    return res.data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
