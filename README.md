# Truce API Backend

This is the backend for the Truce mobile application, focused on tracking product prices in the Egyptian market.

## Base API URL

Once deployed on Render, your API will be available at:
**`https://truce-backend.onrender.com`**

## API Endpoints for Flutter App

These are the direct endpoints you can use in your Flutter application:

### 1. Get All Products (with Prices)
Returns a list of products with their current prices, discounts, and store information.
- **URL**: `https://truce-backend.onrender.com/products`
- **Method**: `GET`
- **Query Parameters**:
  - `search`: (Optional) Search by product name (e.g., `?search=Red Bull`)
  - `category`: (Optional) Filter by category (e.g., `?category=Beverages`)
  - `brand`: (Optional) Filter by brand (e.g., `?brand=Koki`)
  - `store`: (Optional) Filter by store name (e.g., `?store=Carrefour`)
  - `limit`: (Optional) Number of results to return (default: 20, max: 100)
  - `offset`: (Optional) For pagination (default: 0)

### 2. Get Categories
Returns all product categories available in the database.
- **URL**: `https://truce-backend.onrender.com/categories`
- **Method**: `GET`

### 3. Get Stores
Returns all stores tracked by the application.
- **URL**: `https://truce-backend.onrender.com/stores`
- **Method**: `GET`

---

## Features

- **FastAPI Backend**: High-performance API built with Python.
- **Supabase Integration**: Direct connection to Supabase for data storage and retrieval.
- **Data Mapping**: Returns JSON in the specific format required for the Flutter mobile app.
- **Filtering**: Search by product name, category, brand, and store.
- **Daily Scraper**: Included GitHub Action to run a data collection script daily for free.

## Deployment on Render

1. Create a new "Web Service" on Render.
2. Connect this repository.
3. Choose **Python 3** as the runtime.
4. Set the following environment variables in the Render dashboard:
   - `SUPABASE_URL`: https://mgqcolwglaavwazjwjir.supabase.co
   - `SUPABASE_KEY`: sb_publishable_52t3OZTL4k39wQf8DfrH_g_X7n73_vE
5. Render will automatically use the `Procfile` and `requirements.txt` to build and start the server.

## Daily Updates (GitHub Actions)

The repository includes a GitHub Action (`.github/workflows/daily_scraper.yml`) that runs the `scraper.py` script every day at midnight for free.
The credentials for Supabase are already configured in the workflow.

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   SUPABASE_URL=https://mgqcolwglaavwazjwjir.supabase.co SUPABASE_KEY=sb_publishable_52t3OZTL4k39wQf8DfrH_g_X7n73_vE uvicorn main:app --reload
   ```
