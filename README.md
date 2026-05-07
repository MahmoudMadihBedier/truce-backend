# Truce API Backend - Egyptian Market Price Tracker

This backend provides a clean API for your Flutter app with real-time price tracking from the Egyptian market.

## Base API URL
Your API is live at: **`https://truce-backend.vercel.app`**

---

## API Endpoints for Flutter

### 1. Get Products (Main)
Returns products sorted by quality (items with images and links come first).
- **URL**: `https://truce-backend.vercel.app/products`
- **Response Format**: Exact JSON schema requested (Sr No, Price, Product URL, etc.)
- **Filters**: `search`, `category`, `brand`, `store`.

### 2. Get Categories
- **URL**: `https://truce-backend.vercel.app/categories`

### 3. Get Stores
- **URL**: `https://truce-backend.vercel.app/stores`

---

## How it Works (Web Scraping vs Crawling)

### 1. Daily Scraping (Free)
The project includes a **GitHub Action** that runs every night. It uses `scraper.py` to visit Jumia Egypt and other stores, extract the latest prices and images, and save them to your Supabase database.

### 2. Real Price & Image Data
The scraper is designed to:
- Extract the **real price** and **MRP** in EGP.
- Capture the **exact product link** for Jumia/Amazon.
- Get the **high-quality product image**.
- Populate your Supabase tables (`products`, `product_prices`) automatically.

### 3. Smart API Logic
The API in `main.py` doesn't just return random rows. It:
- **Prioritizes Quality**: Items with images and valid links are shown first.
- **Interleaves Stores**: Mixes products from Amazon, Jumia, and Carrefour so the user sees a variety.
- **Calculates Discounts**: Automatically calculates the "Discount %" if not provided by the store.

---

## Deployment & Automation

1. **Hosting**: Hosted on **Vercel** (Free).
2. **Database**: Connected to your **Supabase** project.
3. **Daily Updates**: Managed by **GitHub Actions** (`daily_scraper.yml`).

To add more stores:
Edit `scraper.py` and add a new function for Amazon or Carrefour using the same logic as `scrape_jumia_category`.
