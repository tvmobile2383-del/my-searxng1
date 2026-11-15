import os

SEARXNG_URL = os.getenv("SEARXNG_URL", "").strip().rstrip("/")
STOCK_API_URL = os.getenv("STOCK_API_URL", "").strip().rstrip("/")
STOCK_API_TOKEN = os.getenv("STOCK_API_TOKEN", "").strip()
STOCK_API_PATH = os.getenv("STOCK_API_PATH", "/analyze").strip()
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))
