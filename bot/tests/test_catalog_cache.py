import asyncio

from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import SendMessage

from bot.handlers import catalog_common


def _reset_catalog_cache_state():
    catalog_common.categories_cache.clear()
    catalog_common.subcategories_cache.clear()
    catalog_common.category_lists_cache.clear()
    catalog_common.subcategory_lists_cache.clear()
    catalog_common.catalog_warmup_expires_at = 0.0
    catalog_common.catalog_warmup_task = None


def test_get_categories_cached_uses_local_cache_and_populates_lookup(monkeypatch):
    calls = {"categories": 0}
    _reset_catalog_cache_state()

    async def fake_get_categories():
        calls["categories"] += 1
        return [
            {"id": 1, "name": "Phones"},
            {"id": 2, "name": "Laptops"},
        ]

    monkeypatch.setattr(catalog_common, "get_categories", fake_get_categories)

    first = asyncio.run(catalog_common.get_categories_cached(force_refresh=True))
    second = asyncio.run(catalog_common.get_categories_cached())

    assert first == second
    assert calls["categories"] == 1
    assert catalog_common.categories_cache == {1: "Phones", 2: "Laptops"}


def test_warm_catalog_cache_prefetches_subcategories(monkeypatch):
    calls = {"categories": 0, "subcategories": []}
    _reset_catalog_cache_state()

    async def fake_get_categories():
        calls["categories"] += 1
        return [
            {"id": 10, "name": "Phones"},
            {"id": 20, "name": "Laptops"},
        ]

    async def fake_get_subcategories(cat_id):
        calls["subcategories"].append(cat_id)
        return [
            {"id": cat_id + 1, "name": f"Sub {cat_id}", "category_id": cat_id},
        ]

    monkeypatch.setattr(catalog_common, "get_categories", fake_get_categories)
    monkeypatch.setattr(catalog_common, "get_subcategories", fake_get_subcategories)

    asyncio.run(catalog_common.warm_catalog_cache(force_refresh=True))

    assert calls["categories"] == 1
    assert set(calls["subcategories"]) == {10, 20}
    assert catalog_common.categories_cache == {10: "Phones", 20: "Laptops"}
    assert catalog_common.subcategories_cache[11]["category_id"] == 10
    assert catalog_common.subcategories_cache[21]["category_id"] == 20


def test_safe_callback_answer_uses_short_timeout():
    calls = {}

    class FakeCallback:
        data = "cat_1"
        from_user = type("User", (), {"id": 7})()

        async def answer(self, **kwargs):
            calls.update(kwargs)

    result = asyncio.run(catalog_common.safe_callback_answer(FakeCallback()))

    assert result is True
    assert calls["text"] is None
    assert calls["request_timeout"] == catalog_common.CALLBACK_ACK_TIMEOUT_SECONDS


def test_safe_callback_answer_ignores_network_errors():
    class FakeCallback:
        data = "cat_1"
        from_user = type("User", (), {"id": 7})()

        async def answer(self, **kwargs):
            raise TelegramNetworkError(
                method=SendMessage(chat_id=1, text="test"),
                message="timeout",
            )

    result = asyncio.run(catalog_common.safe_callback_answer(FakeCallback()))

    assert result is False
