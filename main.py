import os
import random
import asyncio
from typing import List, Optional, Union
from fastapi import FastAPI, Query, HTTPException
from dotenv import load_dotenv

# Import our live scrapers
import scraper

load_dotenv()

app = FastAPI(
    title="Truce API",
    description="Backend API with Live Real-time Scraping for the Egyptian Market",
    version="3.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Truce API v3.0.0 - Pure Live Scraping (No Database)"}

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
        # For version 3.0, we ALWAYS use live scraping if search is provided
        # If no search is provided, we use default keywords to show some products
        query_term = search or category or "coffee"

        print(f"[*] Triggering Live Search for: {query_term}")
        loop = asyncio.get_event_loop()

        # Scrape concurrently
        jumia_data, amazon_data = await asyncio.gather(
            loop.run_in_executor(None, scraper.scrape_jumia_live, query_term),
            loop.run_in_executor(None, scraper.scrape_amazon_live, query_term)
        )

        # Combine and interleave
        combined = []
        max_len = max(len(jumia_data), len(amazon_data))
        for i in range(max_len):
            if i < len(jumia_data): combined.append(jumia_data[i])
            if i < len(amazon_data): combined.append(amazon_data[i])

        # Filter by store if requested
        if store:
            combined = [item for item in combined if store.lower() in item["Store Name"].lower()]

        # Re-index Sr No
        for i, item in enumerate(combined):
            item["Sr No"] = i + 1 + offset

        return combined[:limit]

    except Exception as e:
        return {"error": str(e)}

@app.get("/categories")
async def get_categories():
    return [
        {"id": 1, "name_en": "Electronics & Tech"},
        {"id": 2, "name_en": "Home Appliances"},
        {"id": 3, "name_en": "Groceries & Food"},
        {"id": 4, "name_en": "Personal Care & Beauty"},
        {"id": 5, "name_en": "Fashion & Clothing"}
    ]

@app.get("/stores")
async def get_stores():
    return [
        {"id": 1, "name_en": "Amazon", "location": "Online"},
        {"id": 2, "name_en": "Jumia", "location": "Online"},
        {"id": 3, "name_en": "Carrefour", "location": "Egypt Wide"},
        {"id": 4, "name_en": "Noon", "location": "Online"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
