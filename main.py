import os
import json
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Truce API",
    description="Backend API for Truce mobile app - Egyptian Market Price Tracker",
    version="3.0.0"
)

# Load data from the local JSON file
def load_products_data():
    file_path = os.path.join(os.path.dirname(__file__), "products_data.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Truce API - Egyptian Market tracker"}

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
        products = load_products_data()

        # Filtering logic
        filtered_products = products

        if search:
            search = search.lower()
            filtered_products = [p for p in filtered_products if search in p["Product Name"].lower() or search in p["Description"].lower()]

        if category:
            category = category.lower()
            filtered_products = [p for p in filtered_products if category in p["Category"].lower()]

        if brand:
            brand = brand.lower()
            filtered_products = [p for p in filtered_products if brand in p["Brand"].lower()]

        if store:
            store = store.lower()
            filtered_products = [p for p in filtered_products if store in p["Store Name"].lower()]

        # Pagination
        results = filtered_products[offset : offset + limit]

        # Ensure Sr No is correct for the current result set
        for i, p in enumerate(results):
            p["Sr No"] = i + 1 + offset

        return results

    except Exception as e:
        return {"error": str(e)}

@app.get("/categories")
async def get_categories():
    products = load_products_data()
    # Extract unique categories
    categories = sorted(list(set([p["Category"] for p in products])))
    return [{"id": i+1, "name": cat} for i, cat in enumerate(categories)]

@app.get("/stores")
async def get_stores():
    return [
        {"name": "Jumia Egypt", "url": "https://www.jumia.com.eg"},
        {"name": "Amazon Egypt", "url": "https://www.amazon.eg"},
        {"name": "Noon Egypt", "url": "https://www.noon.com/egypt-en/"},
        {"name": "Carrefour Egypt", "url": "https://www.carrefouregypt.com"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
