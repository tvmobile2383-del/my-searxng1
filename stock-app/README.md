# India Stock Discovery & AE8/AE11 Analysis

A separate Streamlit service for Indian stock discovery, selection and Qwen-powered research. It does not replace or modify the existing SearXNG service.

## Features in this first version

- SearXNG search for Indian quarterly-result announcements (search leads only; verify filings).
- Fundamental screening over a starter NSE symbol universe.
- CSV upload to extend the symbol universe (`symbol` column recommended).
- Shortlist management.
- Market snapshot via `yfinance`.
- Company evidence search through SearXNG.
- Full AE8/AE11 analysis prompt sent to the configured Qwen API.
- Multi-stock comparison page.

## Render deployment (separate service)

1. Push the contents of this folder to a new GitHub repository, **or** keep it in the existing repository as `stock-app/`.
2. In Render choose **New + → Web Service → connect the same GitHub repository**.
3. If using the existing repository, set **Root Directory** to `stock-app`. If you created a separate repository containing these files at its root, leave Root Directory blank.
4. Choose **Docker** as the runtime. Render will use this folder's `Dockerfile`.
5. Create the service. Do not change, redeploy or replace the existing SearXNG service.
6. In the new Streamlit Render service, add environment variables:
   - `SEARXNG_URL` = your existing SearXNG public base URL, e.g. `https://your-searxng-service.onrender.com` (no `/search` suffix)
   - `STOCK_API_URL` = your Cloudflare public base URL for the Qwen API (base URL only)
   - `STOCK_API_TOKEN` = the same token configured in the Qwen API server
   - `STOCK_API_PATH` = `/analyze` only if that is the actual route exposed by your Qwen API; otherwise set the correct path.
   - `REQUEST_TIMEOUT` = `120` (optional)
7. Save changes and deploy. Open the new Render URL.

## Important Qwen API contract

The app currently sends:

`POST {STOCK_API_URL}{STOCK_API_PATH}`

Headers:
- `Authorization: Bearer <STOCK_API_TOKEN>`
- `X-API-Token: <STOCK_API_TOKEN>`

JSON body:
```json
{
  "prompt": "full analysis prompt",
  "stock": {"symbol": "RELIANCE", "...": "..."}
}
```

The response should be JSON with one of these text fields: `analysis`, `response`, `result`, `output`, or `text`.

**Before deployment, confirm the actual endpoint path and request/response schema in your existing FastAPI/Qwen server.** If it differs, update `modules/analysis_engine.py` or set `STOCK_API_PATH`. Do not assume the route is `/analyze` unless your API code defines it.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set environment variables before running locally.

## Data and investment limitations

- The result-discovery search is not a structured exchange filing feed. It returns search leads; manually verify the announcement and reporting period.
- `yfinance` is a convenient prototype data source, not a guaranteed official or real-time NSE/BSE feed. It may omit quarterly statements, ratios or symbols.
- A missing value is not zero. The analysis prompt tells the model not to invent unavailable values.
- Reports are research assistance, not investment advice. Verify all data and source documents.
