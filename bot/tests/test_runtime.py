import asyncio
from types import SimpleNamespace

from bot import runtime


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
