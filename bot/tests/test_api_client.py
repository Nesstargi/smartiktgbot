import asyncio
from types import SimpleNamespace

from bot import api_client


def test_get_categories_force_refresh_bypasses_cached_json(monkeypatch):
    calls = {"get_json": 0, "set_json": 0, "http": 0}

    async def fake_get_json(key):
        calls["get_json"] += 1
        return [{"id": 1, "name": "Stale"}]

    async def fake_set_json(key, value, ttl):
        calls["set_json"] += 1

    class FakeResponse:
        def raise_for_status(self):
            return None

        async def json(self):
            return [{"id": 2, "name": "Fresh"}]

    class FakeRequestContext:
        async def __aenter__(self):
            calls["http"] += 1
            return FakeResponse()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        def get(self, url):
            return FakeRequestContext()

    async def fake_get_session():
        return FakeSession()

    monkeypatch.setattr(api_client.runtime_store, "get_json", fake_get_json)
    monkeypatch.setattr(api_client.runtime_store, "set_json", fake_set_json)
    monkeypatch.setattr(api_client, "_get_session", fake_get_session)

    result = asyncio.run(api_client.get_categories(force_refresh=True))

    assert result == [{"id": 2, "name": "Fresh"}]
    assert calls["get_json"] == 0
    assert calls["http"] == 1
    assert calls["set_json"] == 1


def test_get_categories_uses_cached_json_without_force_refresh(monkeypatch):
    calls = {"get_json": 0, "http": 0}

    async def fake_get_json(key):
        calls["get_json"] += 1
        return [{"id": 1, "name": "Cached"}]

    class FakeSession:
        def get(self, url):
            calls["http"] += 1
            raise AssertionError("HTTP should not be called when cache is valid")

    async def fake_get_session():
        return FakeSession()

    monkeypatch.setattr(api_client.runtime_store, "get_json", fake_get_json)
    monkeypatch.setattr(api_client, "_get_session", fake_get_session)

    result = asyncio.run(api_client.get_categories())

    assert result == [{"id": 1, "name": "Cached"}]
    assert calls["get_json"] == 1
    assert calls["http"] == 0


def test_get_subcategories_force_refresh_ignores_cached_json(monkeypatch):
    calls = {"get_json": 0, "http": 0}

    async def fake_get_json(key):
        calls["get_json"] += 1
        return [{"id": 10, "name": "Old", "category_id": 5}]

    async def fake_set_json(key, value, ttl):
        return None

    class FakeResponse:
        def raise_for_status(self):
            return None

        async def json(self):
            return [{"id": 11, "name": "New", "category_id": 5}]

    class FakeRequestContext:
        async def __aenter__(self):
            calls["http"] += 1
            return FakeResponse()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        def get(self, url):
            return FakeRequestContext()

    async def fake_get_session():
        return FakeSession()

    monkeypatch.setattr(api_client.runtime_store, "get_json", fake_get_json)
    monkeypatch.setattr(api_client.runtime_store, "set_json", fake_set_json)
    monkeypatch.setattr(api_client, "_get_session", fake_get_session)

    result = asyncio.run(api_client.get_subcategories(5, force_refresh=True))

    assert result == [{"id": 11, "name": "New", "category_id": 5}]
    assert calls["get_json"] == 0
    assert calls["http"] == 1


def test_get_promotions_force_refresh_bypasses_cached_json(monkeypatch):
    calls = {"get_json": 0, "set_json": 0, "http": 0}

    async def fake_get_json(key):
        calls["get_json"] += 1
        return [{"id": 1, "title": "Old", "is_active": True}]

    async def fake_set_json(key, value, ttl):
        calls["set_json"] += 1

    class FakeResponse:
        def raise_for_status(self):
            return None

        async def json(self):
            return [{"id": 2, "title": "Fresh", "is_active": True}]

    class FakeRequestContext:
        async def __aenter__(self):
            calls["http"] += 1
            return FakeResponse()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        def get(self, url):
            return FakeRequestContext()

    async def fake_get_session():
        return FakeSession()

    monkeypatch.setattr(api_client.runtime_store, "get_json", fake_get_json)
    monkeypatch.setattr(api_client.runtime_store, "set_json", fake_set_json)
    monkeypatch.setattr(api_client, "_get_session", fake_get_session)

    result = asyncio.run(api_client.get_promotions(force_refresh=True))

    assert result == [{"id": 2, "title": "Fresh", "is_active": True}]
    assert calls["get_json"] == 0
    assert calls["http"] == 1
    assert calls["set_json"] == 1


def test_get_bot_settings_force_refresh_bypasses_cached_json(monkeypatch):
    calls = {"get_json": 0, "set_json": 0, "http": 0}

    async def fake_get_json(key):
        calls["get_json"] += 1
        return {"start_message": "Old"}

    async def fake_set_json(key, value, ttl):
        calls["set_json"] += 1

    class FakeResponse:
        def raise_for_status(self):
            return None

        async def json(self):
            return {"start_message": "Fresh"}

    class FakeRequestContext:
        async def __aenter__(self):
            calls["http"] += 1
            return FakeResponse()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        def get(self, url):
            return FakeRequestContext()

    async def fake_get_session():
        return FakeSession()

    monkeypatch.setattr(api_client.runtime_store, "get_json", fake_get_json)
    monkeypatch.setattr(api_client.runtime_store, "set_json", fake_set_json)
    monkeypatch.setattr(api_client, "_get_session", fake_get_session)

    result = asyncio.run(api_client.get_bot_settings(force_refresh=True))

    assert result == {"start_message": "Fresh"}
    assert calls["get_json"] == 0
    assert calls["http"] == 1
    assert calls["set_json"] == 1


def test_get_bot_admin_overview_uses_bot_headers(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        async def json(self):
            return {"bot_users": 9, "leads_total": 3, "recent_leads": []}

    class FakeRequestContext:
        async def __aenter__(self):
            return FakeResponse()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        def get(self, url, headers=None):
            captured["url"] = url
            captured["headers"] = headers
            return FakeRequestContext()

    async def fake_get_session():
        return FakeSession()

    monkeypatch.setattr(api_client, "_get_session", fake_get_session)
    monkeypatch.setattr(api_client, "BOT_API_TOKEN", "secret-token")

    result = asyncio.run(api_client.get_bot_admin_overview(limit=5))

    assert result == {"bot_users": 9, "leads_total": 3, "recent_leads": []}
    assert captured["url"].endswith("/api/bot-admin/overview?limit=5")
    assert captured["headers"] == {"X-Bot-Token": "secret-token"}
