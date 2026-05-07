# Truce API Backend - Egypt Market Scraper & API

This is a database-free, pure scraping backend for the Truce mobile application. It tracks product prices across Jumia, Amazon, Noon, and Carrefour Egypt.

## Architecture

This system uses a **GitHub-to-Vercel** pipeline:
1. **Scraper (`scraper.py`)**: A Python script that visits Jumia and Amazon Egypt to extract the latest product data.
2. **GitHub Actions**: Runs the scraper daily, saves the data to `products_data.json`, and commits it back to the repository.
3. **Vercel API (`main.py`)**: A FastAPI server that reads the JSON file and serves it to your Flutter app.

---

## API Base URL
Your API is live at: **`https://truce-backend.vercel.app`**

### Endpoints

- `GET /products`: List all products.
  - Query Params: `search`, `category`, `brand`, `store`, `limit`, `offset`.
- `GET /categories`: List all detected categories.
- `GET /stores`: List supported Egyptian stores.

---

## Technical Details

- **Language**: Python 3.10
- **Framework**: FastAPI
- **Scraping**: BeautifulSoup4 + Requests
- **Hosting**: Vercel (Free Tier)
- **Automation**: GitHub Actions (Free Tier)

## How to update data manually
You can trigger the scraper by going to the **Actions** tab in your GitHub repository and clicking **Run workflow** on the "Daily Egyptian Market Scraper".
