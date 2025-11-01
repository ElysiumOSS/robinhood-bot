"""This module contains a mapping from stock tickers to company names."""

from __future__ import annotations

import functools
import json
import os
import pathlib
import urllib.error
import urllib.request

# 1) your legacy/static fallback
_STATIC_TICKER_TO_COMPANY = {
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
#    - IEX Cloud has /ref-data/symbols: returns *all* symbols with names, but needs a token. :contentReference[oaicite:0]{index=0}
#    - Yahoo-style unofficial endpoints can give you company info by ticker. :contentReference[oaicite:1]{index=1}
#    Below is a tiny Yahoo-like fetcher (no extra deps). Swap with IEX if you prefer.


def _fetch_name_from_yahoo(ticker: str) -> str | None:
    """
    Fetch company name for a ticker from a Yahoo-like endpoint.
    This mirrors the idea shown in multiple Yahoo Finance examples. :contentReference[oaicite:2]{index=2}
    """
    # endpoint that returns quote summary-ish JSON; there are many variants in the wild
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=price"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

    try:
        return data["quoteSummary"]["result"][0]["price"]["longName"]
    except (KeyError, TypeError, IndexError):
        # some tickers only have shortName
        try:
            return data["quoteSummary"]["result"][0]["price"]["shortName"]
        except (KeyError, TypeError, IndexError):
            return None


def _fetch_all_from_iex() -> dict[str, str]:
    """
    Fetch ALL symbols from IEX Cloud and build a dict.
    Needs IEX_TOKEN in env. :contentReference[oaicite:3]{index=3}
    """
    token = os.getenv("IEX_TOKEN")
    if not token:
        return {}

    url = f"https://cloud.iexapis.com/stable/ref-data/symbols?token={token}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            rows = json.load(resp)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return {}

    # rows look like: {"symbol": "AAPL", "name": "Apple Inc.", ...}
    return {row["symbol"].upper(): row.get("name", "").strip() for row in rows if row.get("symbol")}


# 4) file cache helpers --------------------------------------------------------
def _load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (KeyError, TypeError, IndexError):
            return {}
    return {}


def _save_cache(cache: dict[str, str]) -> None:
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
    2. remote (IEX if token, else Yahoo)
    3. static fallback
    """
    t = ticker.upper().strip()

    # 1) check file cache
    cache = _load_cache()
    if t in cache and cache[t]:
        return cache[t]

    # 2) try remote
    name = None
    # prefer IEX if you have a token
    iex_map = _fetch_all_from_iex()
    if iex_map and t in iex_map:
        name = iex_map[t]
    else:
        # otherwise try yahoo-style single lookup
        name = _fetch_name_from_yahoo(t)

    if name:
        cache[t] = name
        _save_cache(cache)
        return name

    # 3) final fallback
    return _STATIC_TICKER_TO_COMPANY.get(t)


# 6) if you still want a dict-like object:
class DynamicTickerMap(dict):
    """
    dict-ish object that resolves missing tickers dynamically.
    """

    def __missing__(self, key: str) -> str:
        name = get_company_name(key)
        if name is None:
            raise KeyError(key)
        # cache in the instance too
        self[key] = name
        return name


TICKER_TO_COMPANY = DynamicTickerMap(_STATIC_TICKER_TO_COMPANY)
