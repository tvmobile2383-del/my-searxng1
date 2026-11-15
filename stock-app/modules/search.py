import requests
from modules.config import SEARXNG_URL, REQUEST_TIMEOUT

def search_web(query: str, limit: int = 8):
    if not SEARXNG_URL:
        raise RuntimeError("Set SEARXNG_URL in Render environment variables.")
    response = requests.get(
        f"{SEARXNG_URL}/search",
        params={"q": query, "format": "json", "language": "en-IN"},
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": "IndiaStockDiscovery/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    return [{
        "title": x.get("title", ""),
        "content": x.get("content", ""),
        "url": x.get("url", ""),
        "publishedDate": x.get("publishedDate", ""),
        "engine": x.get("engine", ""),
    } for x in payload.get("results", [])[:limit]]

def result_search_queries(period: str):
    timeframe = {"Today": "today", "Last 3 days": "in the last 3 days",
                 "Last 7 days": "in the last 7 days"}[period]
    return [
        f"India NSE BSE listed companies quarterly results declared {timeframe}",
        f"Indian companies financial results announced {timeframe} NSE BSE",
        f"NSE corporate announcements financial results {timeframe}",
    ]
