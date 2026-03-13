import os
import time
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

_session: aiohttp.ClientSession | None = None
_cache: dict[str, tuple[float, object]] = {}


DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=8)


def _url(path: str) -> str:
    return f"{API_URL}{path}"


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        connector = aiohttp.TCPConnector(limit=30, ttl_dns_cache=300)
        _session = aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT, connector=connector)
    return _session


def _cache_get(key: str):
    hit = _cache.get(key)
    if not hit:
        return None
    expires_at, value = hit
    if expires_at < time.monotonic():
        _cache.pop(key, None)
        return None
    return value


def _cache_set(key: str, value, ttl_seconds: int):
    _cache[key] = (time.monotonic() + ttl_seconds, value)


async def _get(path: str, cache_seconds: int = 0):
    key = f"GET:{path}"
    if cache_seconds > 0:
        cached = _cache_get(key)
        if cached is not None:
            return cached

    session = await _get_session()
    async with session.get(_url(path)) as resp:
        resp.raise_for_status()
        data = await resp.json()

    if cache_seconds > 0:
        _cache_set(key, data, cache_seconds)
    return data


async def fetch_bytes(url: str, cache_seconds: int = 60) -> bytes | None:
    key = f"BYTES:{url}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    session = await _get_session()
    async with session.get(url) as resp:
        if resp.status != 200:
            return None
        data = await resp.read()

    if not data:
        return None

    if cache_seconds > 0:
        _cache_set(key, data, cache_seconds)
    return data


async def get_categories():
    return await _get("/api/categories", cache_seconds=120)


async def get_subcategories(cat_id: int):
    return await _get(f"/api/subcategories/{cat_id}", cache_seconds=120)


async def get_products(sub_id: int):
    return await _get(f"/api/products/{sub_id}", cache_seconds=60)


async def get_promotions():
    return await _get("/api/promotions", cache_seconds=30)


async def get_bot_settings():
    return await _get("/api/bot-settings", cache_seconds=10)


async def create_lead(payload: dict):
    session = await _get_session()
    async with session.post(_url("/api/leads"), json=payload) as resp:
        resp.raise_for_status()
        return await resp.json()


async def close_http_session():
    global _session
    if _session and not _session.closed:
        await _session.close()
    _session = None
