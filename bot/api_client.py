import os
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

from bot.runtime_store import runtime_store

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
BOT_API_TOKEN = os.getenv("BOT_API_TOKEN", "")
BOT_AUDIENCE_SYNC_TTL_SECONDS = int(os.getenv("BOT_AUDIENCE_SYNC_TTL_SECONDS", "3600"))

_session: aiohttp.ClientSession | None = None


DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=8)


def _url(path: str) -> str:
    return f"{API_URL}{path}"


def _bot_headers():
    return {"X-Bot-Token": BOT_API_TOKEN} if BOT_API_TOKEN else None


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        connector = aiohttp.TCPConnector(limit=50, ttl_dns_cache=300)
        _session = aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT, connector=connector)
    return _session


async def _get(path: str, cache_seconds: int = 0, force_refresh: bool = False):
    key = f"GET:{path}"
    if cache_seconds > 0 and not force_refresh:
        cached = await runtime_store.get_json(f"api:json:{key}")
        if cached is not None:
            return cached

    session = await _get_session()
    async with session.get(_url(path)) as resp:
        resp.raise_for_status()
        data = await resp.json()

    if cache_seconds > 0:
        await runtime_store.set_json(f"api:json:{key}", data, cache_seconds)
    return data


async def fetch_bytes(url: str, cache_seconds: int = 300) -> bytes | None:
    key = f"BYTES:{url}"
    cached = await runtime_store.get_bytes(f"api:bytes:{key}")
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
        await runtime_store.set_bytes(f"api:bytes:{key}", data, cache_seconds)
    return data


async def get_categories(force_refresh: bool = False):
    return await _get("/api/categories", cache_seconds=300, force_refresh=force_refresh)


async def get_subcategories(cat_id: int, force_refresh: bool = False):
    return await _get(
        f"/api/subcategories/{cat_id}",
        cache_seconds=300,
        force_refresh=force_refresh,
    )


async def get_products(sub_id: int, force_refresh: bool = False):
    return await _get(
        f"/api/products/{sub_id}",
        cache_seconds=180,
        force_refresh=force_refresh,
    )


async def get_promotions(force_refresh: bool = False):
    return await _get("/api/promotions", cache_seconds=60, force_refresh=force_refresh)


async def update_promotion_file_id(promotion_id: int, image_file_id: str):
    if not promotion_id or not image_file_id:
        return None

    session = await _get_session()
    payload = {"image_file_id": image_file_id}
    try:
        async with session.post(
            _url(f"/api/promotions/{promotion_id}/file-id"),
            json=payload,
            headers=_bot_headers(),
        ) as resp:
            if resp.status >= 400:
                return None
            return await resp.json()
    except Exception:
        return None


async def register_bot_subscriber(payload: dict):
    chat_id = payload.get("chat_id")
    if chat_id is None:
        return False

    cache_key = f"bot:audience:registered:{chat_id}"
    if BOT_AUDIENCE_SYNC_TTL_SECONDS > 0:
        cached = await runtime_store.get_text(cache_key)
        if cached == "1":
            return True

    session = await _get_session()
    try:
        async with session.post(
            _url("/api/bot-subscribers/register"),
            json=payload,
            headers=_bot_headers(),
        ) as resp:
            if resp.status >= 400:
                return False
    except Exception:
        return False

    if BOT_AUDIENCE_SYNC_TTL_SECONDS > 0:
        await runtime_store.set_text(cache_key, "1", BOT_AUDIENCE_SYNC_TTL_SECONDS)
    return True


async def get_bot_settings(force_refresh: bool = False):
    return await _get("/api/bot-settings", cache_seconds=20, force_refresh=force_refresh)


async def get_bot_admin_overview(limit: int = 10):
    session = await _get_session()
    async with session.get(
        _url(f"/api/bot-admin/overview?limit={int(limit)}"),
        headers=_bot_headers(),
    ) as resp:
        resp.raise_for_status()
        return await resp.json()


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
