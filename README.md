# Truce API Backend - Multi-Store Egyptian Market Tracker

A comprehensive backend and automated scraping system for tracking product prices across major Egyptian retailers.

## Supported Stores
- **Jumia Egypt** (Full Scraping)
- **Amazon Egypt** (Full Scraping)
- **Noon Egypt** (Search Integration)
- **Carrefour Egypt** (Search Integration)

## API Base URL
**`https://truce-backend.vercel.app`**

### API Endpoints
- `GET /products`: Multi-store products with priority sorting (Images & Links first).
- `GET /categories`: All product categories.
- `GET /stores`: Tracked stores and their ratings.

---

## Automated Scraper (`scraper.py`)

The scraper is designed to run daily for free via **GitHub Actions**. It handles:
1. **Multi-Store Logic**: Separate logic for Jumia, Amazon, etc.
2. **Polite Scraping**: Uses random delays and rotating user-agents to avoid blocks.
3. **Data Quality**: Captures real prices, original prices (MRP), product images, and direct store links.
4. **Database Sync**: Automatically upserts data into your Supabase project.

### How to Trigger Manually
1. Go to your GitHub repository.
2. Click on **Actions**.
3. Select **Daily Product Scraper**.
4. Click **Run workflow**.

## Deployment

### 1. API (Vercel)
- Simply connect your GitHub repo to Vercel.
- It uses `vercel.json` for zero-config deployment.

### 2. Scraper (GitHub Actions)
- Configured in `.github/workflows/daily_scraper.yml`.
- **Credentials** for your Supabase project are already integrated.

---

## Technical Details
- **Backend**: FastAPI (Python)
- **Scraper**: BeautifulSoup4 + Requests
- **Database**: Supabase (PostgreSQL)
- **Automation**: GitHub Actions
