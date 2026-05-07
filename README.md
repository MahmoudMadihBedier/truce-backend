# Truce API Backend

This is the backend for the Truce mobile application, focused on tracking product prices in the Egyptian market.

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
   - `SUPABASE_URL`: Your Supabase project URL.
   - `SUPABASE_KEY`: Your Supabase publishable API key (anon key).
5. Render will automatically use the `Procfile` and `requirements.txt` to build and start the server.

## Daily Updates (GitHub Actions)

The repository includes a GitHub Action (`.github/workflows/daily_scraper.yml`) that runs the `scraper.py` script every day at midnight.

To enable this:
1. Go to your GitHub repository **Settings** > **Secrets and variables** > **Actions**.
2. Add the following secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your Supabase credentials.
3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once running, visit `/docs` or `/redoc` for interactive API documentation.

- `GET /products`: List products with filters (`search`, `category`, `brand`, `store`).
- `GET /categories`: List available categories.
- `GET /stores`: List available stores.
