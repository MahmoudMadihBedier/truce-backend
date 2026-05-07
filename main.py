import os
import random
from typing import List, Optional, Union
from fastapi import FastAPI, Query, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Truce API",
    description="Backend API for Truce mobile app - Egyptian Market Price Tracker",
    version="1.5.0"
)

# Constants for Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mgqcolwglaavwazjwjir.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_52t3OZTL4k39wQf8DfrH_g_X7n73_vE")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def transform_product_price(item, index: int):
    product = item.get("product") or {}
    category = product.get("category") or {}
    store = item.get("store") or {}

    store_name = store.get("name_en", "N/A")
    store_urls = {
        "Amazon": "https://www.amazon.eg",
        "Jumia": "https://www.jumia.com.eg",
        "Noon": "https://www.noon.com/egypt-en/",
        "Carrefour": "https://www.carrefouregypt.com"
    }

    mrp_val = item.get("mrp")
    price_val = item.get("price")
    discount_pct = item.get("discount_percent")

    final_price = float(price_val) if price_val is not None else "N/A"
    final_mrp = float(mrp_val) if mrp_val is not None else (final_price if final_price != "N/A" else "N/A")

    if discount_pct is None and isinstance(final_mrp, float) and isinstance(final_price, float) and final_mrp > final_price:
        discount_pct = round(((final_mrp - final_price) / final_mrp) * 100)

    product_url = item.get("product_url") or product.get("source_url") or store_urls.get(store_name, "N/A")
    image_url = product.get("image_url") or "https://via.placeholder.com/300?text=No+Image"

    return {
        "Sr No": index + 1,
        "Product URL": product_url,
        "Product ID": product.get("id", "N/A"),
        "Product Name": product.get("name_en") or "N/A",
        "Category": category.get("name_en") if category else "N/A",
        "Brand": product.get("brand") or "N/A",
        "MRP (EGP)": final_mrp,
        "Discount %": discount_pct if discount_pct is not None else "N/A",
        "Price": final_price,
        "Description": product.get("description_en") or "N/A",
        "Product Image URL": image_url,
        "Store Name": store_name,
        "Location": store.get("location_name_en") or "N/A",
        "Availability Status": "In Stock" if item.get("is_available") else "Out of Stock"
    }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Truce API",
        "status": "online",
        "endpoints": {"products": "/products", "categories": "/categories", "stores": "/stores"}
    }

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
        # Strategy: Prioritize items with image_url and product_url
        query = supabase.table("product_prices").select(
            "*, product:products(*, category:categories(*)), store:stores(*)"
        )

        if search:
            query = query.ilike("product.name_en", f"%{search}%")
        if category:
            query = query.ilike("product.category.name_en", f"%{category}%")
        if brand:
            query = query.ilike("product.brand", f"%{brand}%")
        if store:
            query = query.ilike("store.name_en", f"%{store}%")

        # Fetch enough to filter and interleave
        fetch_limit = 300
        query = query.range(offset, offset + fetch_limit - 1)

        response = query.execute()
        data = response.data

        if not data:
            return []

        # Filter out invalid entries
        valid_data = [item for item in data if item.get("product")]

        # Sort so items with images and URLs come first
        def priority_score(item):
            score = 0
            prod = item.get("product") or {}
            if prod.get("image_url") and "placeholder" not in prod.get("image_url", "").lower():
                score += 10
            if item.get("product_url") or prod.get("source_url"):
                score += 5
            if item.get("price") is not None:
                score += 3
            return score

        valid_data.sort(key=priority_score, reverse=True)

        # Interleave stores for variety among the highest quality results
        store_groups = {}
        for item in valid_data:
            s_name = (item.get("store") or {}).get("name_en", "Other")
            if s_name not in store_groups: store_groups[s_name] = []
            store_groups[s_name].append(item)

        interleaved = []
        if store_groups:
            max_size = max(len(g) for g in store_groups.values())
            for i in range(max_size):
                s_names = list(store_groups.keys())
                # For high quality first, we don't shuffle s_names here,
                # but we could to prevent store bias
                for s_name in sorted(s_names):
                    if i < len(store_groups[s_name]):
                        interleaved.append(store_groups[s_name][i])

        result = [transform_product_price(item, i + offset) for i, item in enumerate(interleaved[:limit])]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    response = supabase.table("categories").select("*").execute()
    return response.data

@app.get("/stores")
async def get_stores():
    response = supabase.table("stores").select("*").execute()
    return response.data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
