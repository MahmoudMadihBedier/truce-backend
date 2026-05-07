# Truce API Backend - Real-Time Live Search

This backend provides real-time product tracking for the Egyptian market by scraping live data from stores like Jumia and Amazon on every search.

## Features

- **Live Real-time Search**: When you search for a product, the API scrapes the stores **instantly** to get the latest price, image, and link.
- **Always Fresh Data**: The API doesn't just rely on the database; it fetches the live store page.
- **Database Auto-Sync**: Every search updates your Supabase database with the latest results, ensuring your data is never old.
- **Exact JSON Format**: Returns the response in your requested Flutter-friendly format.

---

## API Endpoints

### 1. Live Product Search
- **URL**: `/products?search=... `
- **Behavior**: Scrapes Jumia and Amazon Egypt in real-time.
- **Example**: `https://truce-backend.vercel.app/products?search=coffee`

### 2. General Browsing
- **URL**: `/products`
- **Behavior**: Returns recent products from the database.

---

## Technical Flow
1. User sends a search query.
2. API triggers `scraper.py` to visit Jumia and Amazon.
3. Scraper parses the **real prices** and **real images**.
4. Scraper saves/updates these products in **Supabase**.
5. API returns the live results to the Flutter app immediately.

## Deployment

### Vercel (Free)
1. Connect your repo to Vercel.
2. The `vercel.json` and `main.py` are ready for zero-config deployment.

### GitHub Actions (Daily Updates)
- Use the provided `daily_scraper.yml` to run a full market scan every night for free.
