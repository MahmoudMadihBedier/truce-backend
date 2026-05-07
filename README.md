# Truce API Backend

This is the backend for the Truce mobile application, focused on tracking product prices in the Egyptian market.

## Free Hosting Options

You can host this API for free on **Vercel** or **Hugging Face Spaces**.

### Option 1: Vercel (Recommended)
Vercel is very fast and has a generous free tier.
1. Create a free account on [Vercel](https://vercel.com).
2. Click **Add New** > **Project**.
3. Import your GitHub repository.
4. Vercel will automatically detect the configuration from `vercel.json`.
5. Your API will be live at: `https://your-project-name.vercel.app`

### Option 2: Hugging Face Spaces (100% Free & Persistent)
Hugging Face Spaces is great for hosting Python APIs and doesn't require a credit card.
1. Create a free account on [Hugging Face](https://huggingface.co).
2. Click **New** > **Space**.
3. Choose **Docker** as the SDK.
4. Give it a name and set visibility to Public.
5. Hugging Face will automatically use the `Dockerfile` to build and run your API.
6. Your API will be live at: `https://huggingface.co/spaces/your-username/your-space-name`

---

## API Endpoints for Flutter App

These endpoints return data in the exact JSON format required for your mobile app.

### 1. Get All Products (with Prices)
- **URL**: `/products`
- **Method**: `GET`
- **Query Parameters**:
  - `search`: Search by name (e.g., `?search=Red Bull`)
  - `category`: Filter by category (e.g., `?category=Beverages`)
  - `brand`: Filter by brand (e.g., `?brand=Koki`)
  - `store`: Filter by store (e.g., `?store=Carrefour`)
  - `limit`: Number of results (default: 20)

### 2. Get Categories
- **URL**: `/categories`
- **Method**: `GET`

### 3. Get Stores
- **URL**: `/stores`
- **Method**: `GET`

---

## Daily Updates (GitHub Actions)

The repository includes a GitHub Action (`.github/workflows/daily_scraper.yml`) that runs the `scraper.py` script every day at midnight for free using GitHub's infrastructure.

**Credentials are already pre-configured in the code.**

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   python main.py
   ```
