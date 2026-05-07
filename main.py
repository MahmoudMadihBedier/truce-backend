import os
from typing import List, Optional, Union
from fastapi import FastAPI, Query, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Truce API",
    description="Backend API for Truce mobile app - Egyptian Market Price Tracker",
    version="1.0.0"
)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def transform_product_price(item, index: int):
    """
    Transforms Supabase record into the exact JSON format requested by the user.
    """
    product = item.get("product", {}) or {}
    category = product.get("category", {}) or {}
    store = item.get("store", {}) or {}

    # Extract values
    mrp_val = item.get("mrp")
    price_val = item.get("price")
    discount_pct = item.get("discount_percent")

    # Logic for Price and MRP
    # If price is missing but MRP exists, price = MRP (no discount)
    # If both missing, set to "N/A"

    final_price = float(price_val) if price_val is not None else "N/A"
    final_mrp = float(mrp_val) if mrp_val is not None else (final_price if final_price != "N/A" else "N/A")

    # Calculate discount if not provided but MRP and Price exist
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
        # Extra fields requested in the text requirements
        "Store Name": store.get("name_en") or "N/A",
        "Location": store.get("location_name_en") or "N/A",
        "Availability Status": "In Stock" if item.get("is_available") else "Out of Stock"
    }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Truce API",
        "status": "online",
        "endpoints": {
            "products": "/products",
            "categories": "/categories",
            "stores": "/stores"
        }
    }

@app.get("/products")
async def get_products(
    search: Optional[str] = Query(None, description="Search by product name"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    store: Optional[str] = Query(None, description="Filter by store name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = 0
):
    try:
        # Complex join query
        query = supabase.table("product_prices").select(
            "*, product:products(*, category:categories(*)), store:stores(*)"
        )

        # In Supabase, we can filter on joined tables using dot notation
        if search:
            query = query.ilike("product.name_en", f"%{search}%")

        if category:
            query = query.ilike("product.category.name_en", f"%{category}%")

        if brand:
            query = query.ilike("product.brand", f"%{brand}%")

        if store:
            query = query.ilike("store.name_en", f"%{store}%")

        # Ordering by update time or price could be added here
        query = query.order("updated_at", desc=True)

        # Pagination
        query = query.range(offset, offset + limit - 1)

        response = query.execute()
        data = response.data

        result = []
        for i, item in enumerate(data):
            if item.get("product"):
                result.append(transform_product_price(item, i + offset))

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
