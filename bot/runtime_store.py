from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

try:
    from redis.asyncio import Redis
    from redis.asyncio import from_url as redis_from_url
except Exception:  # pragma: no cover - optional dependency fallback
    Redis = None
    redis_from_url = None


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "").strip()
REDIS_PREFIX = os.getenv("REDIS_PREFIX", "smartiktg")
MEMORY_MIRROR_TTL_SECONDS = int(os.getenv("BOT_MEMORY_CACHE_TTL_SECONDS", "60"))


class RuntimeStore:
    def __init__(self):
        self._client: Redis | None = None
        self._memory: dict[str, tuple[float | None, Any]] = {}
        self._redis_failed = False

    def _full_key(self, key: str) -> str:
        return f"{REDIS_PREFIX}:{key}"

    def _memory_get(self, key: str):
        hit = self._memory.get(key)
        if not hit:
            return None

        expires_at, value = hit
        if expires_at is not None and expires_at < time.monotonic():
            self._memory.pop(key, None)
            return None

        return value

    def _memory_set(self, key: str, value: Any, ttl_seconds: int | None = None):
        expires_at = None
        if ttl_seconds is not None and ttl_seconds > 0:
            expires_at = time.monotonic() + ttl_seconds
        self._memory[key] = (expires_at, value)

    def _memory_delete(self, key: str):
        self._memory.pop(key, None)

    async def initialize(self) -> bool:
        client = await self._get_client()
        return client is not None

    async def close(self):
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception:
                logger.debug("Redis client close failed", exc_info=True)
        self._client = None
        self._redis_failed = False

    async def _get_client(self) -> Redis | None:
        if self._client is not None:
            return self._client
        if not REDIS_URL or redis_from_url is None or self._redis_failed:
            return None

        client = redis_from_url(REDIS_URL, encoding=None, decode_responses=False)
        try:
            await client.ping()
        except Exception:
            self._redis_failed = True
            logger.warning("Redis is unavailable, bot will continue with in-memory cache only.")
            try:
                await client.aclose()
            except Exception:
                logger.debug("Redis client close failed after init error", exc_info=True)
            return None

        self._client = client
        logger.info("Redis cache is enabled for bot runtime store.")
        return self._client

    async def get_json(self, key: str):
        cached = self._memory_get(key)
        if cached is not None:
            return cached

        client = await self._get_client()
        if client is None:
            return None

        try:
            raw = await client.get(self._full_key(key))
        except Exception:
            logger.debug("Redis get_json failed for %s", key, exc_info=True)
            return None

        if raw is None:
            return None

        try:
            value = json.loads(raw)
        except Exception:
            logger.debug("Redis returned invalid JSON for %s", key, exc_info=True)
            return None

        self._memory_set(key, value, MEMORY_MIRROR_TTL_SECONDS)
        return value

    async def set_json(self, key: str, value: Any, ttl_seconds: int | None = None):
        self._memory_set(key, value, ttl_seconds or MEMORY_MIRROR_TTL_SECONDS)

        client = await self._get_client()
        if client is None:
            return

        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        try:
            if ttl_seconds and ttl_seconds > 0:
                await client.set(self._full_key(key), raw, ex=ttl_seconds)
            else:
                await client.set(self._full_key(key), raw)
        except Exception:
            logger.debug("Redis set_json failed for %s", key, exc_info=True)

    async def pop_json(self, key: str):
        value = await self.get_json(key)
        await self.delete(key)
        return value

    async def get_text(self, key: str) -> str | None:
        cached = self._memory_get(key)
        if cached is not None:
            return str(cached)

        client = await self._get_client()
        if client is None:
            return None

        try:
            raw = await client.get(self._full_key(key))
        except Exception:
            logger.debug("Redis get_text failed for %s", key, exc_info=True)
            return None

        if raw is None:
            return None

        value = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
        self._memory_set(key, value, MEMORY_MIRROR_TTL_SECONDS)
        return value

    async def set_text(self, key: str, value: str, ttl_seconds: int | None = None):
        self._memory_set(key, value, ttl_seconds or MEMORY_MIRROR_TTL_SECONDS)

        client = await self._get_client()
        if client is None:
            return

        try:
            if ttl_seconds and ttl_seconds > 0:
                await client.set(self._full_key(key), value, ex=ttl_seconds)
            else:
                await client.set(self._full_key(key), value)
        except Exception:
            logger.debug("Redis set_text failed for %s", key, exc_info=True)

    async def get_bytes(self, key: str) -> bytes | None:
        cached = self._memory_get(key)
        if cached is not None:
            return bytes(cached)

        client = await self._get_client()
        if client is None:
            return None

        try:
            raw = await client.get(self._full_key(key))
        except Exception:
            logger.debug("Redis get_bytes failed for %s", key, exc_info=True)
            return None

        if raw is None:
            return None

        value = bytes(raw)
        self._memory_set(key, value, MEMORY_MIRROR_TTL_SECONDS)
        return value

    async def set_bytes(self, key: str, value: bytes, ttl_seconds: int | None = None):
        self._memory_set(key, value, ttl_seconds or MEMORY_MIRROR_TTL_SECONDS)

        client = await self._get_client()
        if client is None:
            return

        try:
            if ttl_seconds and ttl_seconds > 0:
                await client.set(self._full_key(key), value, ex=ttl_seconds)
            else:
                await client.set(self._full_key(key), value)
        except Exception:
            logger.debug("Redis set_bytes failed for %s", key, exc_info=True)

    async def delete(self, key: str):
        self._memory_delete(key)

        client = await self._get_client()
        if client is None:
            return

        try:
            await client.delete(self._full_key(key))
        except Exception:
            logger.debug("Redis delete failed for %s", key, exc_info=True)

    async def scan_json(self, prefix: str) -> dict[str, Any]:
        results: dict[str, Any] = {}

        for key in list(self._memory.keys()):
            if not key.startswith(prefix):
                continue
            value = self._memory_get(key)
            if value is not None:
                results[key] = value

        client = await self._get_client()
        if client is None:
            return results

        try:
            async for full_key in client.scan_iter(match=self._full_key(f"{prefix}*")):
                short_key = full_key.decode("utf-8") if isinstance(full_key, bytes) else str(full_key)
                short_key = short_key.removeprefix(f"{REDIS_PREFIX}:")
                raw = await client.get(full_key)
                if raw is None:
                    continue
                value = json.loads(raw)
                self._memory_set(short_key, value, MEMORY_MIRROR_TTL_SECONDS)
                results[short_key] = value
        except Exception:
            logger.debug("Redis scan_json failed for prefix %s", prefix, exc_info=True)

        return results


runtime_store = RuntimeStore()
