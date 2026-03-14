import asyncio
import socket
from types import SimpleNamespace

from bot import runtime


def test_get_bot_instance_builds_bot_with_configured_session(monkeypatch):
    captured = {}
    fake_session = SimpleNamespace(_connector_init={})

    def fake_session_factory(**kwargs):
        captured["session_kwargs"] = kwargs
        return fake_session

    class FakeBot:
        def __init__(self, token, session):
            captured["token"] = token
            captured["bot_session"] = session
            self.session = SimpleNamespace()

    monkeypatch.setattr(runtime, "TOKEN", "123:ABC")
    monkeypatch.setattr(runtime, "_bot", None)
    monkeypatch.setattr(runtime, "TELEGRAM_FORCE_IPV4", True)
    monkeypatch.setattr(runtime, "TELEGRAM_BOT_REQUEST_TIMEOUT_SECONDS", 20.0)
    monkeypatch.setattr(runtime, "TELEGRAM_BOT_CONNECTOR_LIMIT", 20)
    monkeypatch.setattr(runtime, "AiohttpSession", fake_session_factory)
    monkeypatch.setattr(runtime, "Bot", FakeBot)

    bot = runtime.get_bot_instance()

    assert bot is not None
    assert captured["token"] == "123:ABC"
    assert captured["bot_session"] is fake_session
    assert captured["session_kwargs"]["timeout"] == 20.0
    assert captured["session_kwargs"]["limit"] == 20
    assert captured["bot_session"]._connector_init["family"] == socket.AF_INET


def test_get_bot_instance_reuses_existing_bot_without_closed_attribute(monkeypatch):
    fake_bot = SimpleNamespace(session=SimpleNamespace())

    monkeypatch.setattr(runtime, "TOKEN", "123:ABC")
    monkeypatch.setattr(runtime, "_bot", fake_bot)

    assert runtime.get_bot_instance() is fake_bot


def test_shutdown_bot_runtime_closes_session_without_closed_attribute(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.close_calls = 0

        async def close(self):
            self.close_calls += 1

    session = FakeSession()
    fake_bot = SimpleNamespace(session=session)

    async def fake_close_http_session():
        return None

    async def fake_store_close():
        return None

    async def fake_shutdown_background_tasks():
        return None

    monkeypatch.setattr(runtime, "_bot", fake_bot)
    monkeypatch.setattr(runtime, "_runtime_started", True)
    monkeypatch.setattr(runtime, "close_http_session", fake_close_http_session)
    monkeypatch.setattr(runtime, "shutdown_background_tasks", fake_shutdown_background_tasks)
    monkeypatch.setattr(runtime.runtime_store, "close", fake_store_close)

    asyncio.run(runtime.shutdown_bot_runtime())

    assert session.close_calls == 1
    assert runtime._bot is None
    assert runtime._runtime_started is False
