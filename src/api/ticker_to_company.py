"""This module contains a mapping from stock tickers to company names."""

from __future__ import annotations

import functools
import json
import os
import pathlib
import urllib.error
import urllib.request

# 1) your legacy/static fallback
_STATIC_TICKER_TO_COMPANY: dict[str, str] = {
    "AAPL": "Apple Inc",
    "GOOGL": "Alphabet Inc",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com Inc",
    "META": "Meta Platforms Inc",
    "TSLA": "Tesla Inc",
    "NVDA": "NVIDIA Corporation",
    "NFLX": "Netflix Inc",
    "IBM": "International Business Machines",
    "INTC": "Intel Corporation",
}

# 2) optional: local cache file so you don't hit the network every run
CACHE_PATH = pathlib.Path(".ticker_cache.json")

# 3) pick a remote source
#    - Alpha Vantage unofficial endpoints can give you company info by ticker.
#    Below is a tiny Alpha Vantage-like fetcher (no extra deps).


def _fetch_name_from_alpha_vantage(ticker: str) -> str | None:
    """
    Fetch company name for a ticker from a Alpha Vantage-like endpoint.
    This mirrors the idea shown in multiple Alpha Vantage Finance examples.
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return None

    # endpoint that returns quote summary-ish JSON; there are many variants in the wild
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    try:
        return data["Name"]
    except (KeyError, TypeError, IndexError):
        return None


# 4) file cache helpers --------------------------------------------------------
def _load_cache() -> dict[str, str]:
    """Load the ticker cache from a local file, safely handling errors."""
    if not CACHE_PATH.is_file():
        return {}
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        # Filter for string keys and non-empty string values to ensure type safety
        return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str) and v}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict[str, str]) -> None:
    """Save the ticker cache to a local file."""
    try:
        CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
    except (OSError, ValueError):
        # cache is best-effort
        pass


# 5) public API ----------------------------------------------------------------
@functools.lru_cache(maxsize=2048)
def get_company_name(ticker: str) -> str | None:
    """
    Get the company name for a ticker, trying:
    1. in-memory/file cache
    2. remote (Alpha Vantage)
    3. static fallback
    """
    t = ticker.upper().strip()
    if not t:
        return None

    # 1) check file cache
    cache = _load_cache()
    if t in cache:
        return cache[t]

    # 2) try remote
    name = _fetch_name_from_alpha_vantage(t)

    if name:
        cache[t] = name
        _save_cache(cache)
        return name

    # 3) final fallback
    return _STATIC_TICKER_TO_COMPANY.get(t)


# 6) if you still want a dict-like object:
class DynamicTickerMap(dict[str, str]):
    """
    dict-ish object that resolves missing tickers dynamically.
    """

    def __missing__(self, key: str) -> str:
        if not isinstance(key, str):
            raise KeyError(key)
        name = get_company_name(key)
        if name is None:
            raise KeyError(f"Ticker '{key}' not found")
        # cache in the instance too
        self[key] = name
        return name


TICKER_TO_COMPANY = DynamicTickerMap(_STATIC_TICKER_TO_COMPANY)
