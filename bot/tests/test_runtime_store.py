import asyncio

from bot.runtime_store import RuntimeStore


def test_runtime_store_uses_memory_fallback_for_json_and_text():
    store = RuntimeStore()
    store._redis_failed = True

    asyncio.run(store.set_json("state:user:1", {"chat_id": 10, "flow": "consultation"}, 30))
    asyncio.run(store.set_text("flag:user:1", "1", 30))

    assert asyncio.run(store.get_json("state:user:1")) == {
        "chat_id": 10,
        "flow": "consultation",
    }
    assert asyncio.run(store.get_text("flag:user:1")) == "1"

    popped = asyncio.run(store.pop_json("state:user:1"))
    assert popped == {"chat_id": 10, "flow": "consultation"}
    assert asyncio.run(store.get_json("state:user:1")) is None


def test_runtime_store_uses_memory_fallback_for_bytes_and_scan():
    store = RuntimeStore()
    store._redis_failed = True

    asyncio.run(store.set_bytes("api:bytes:/banner", b"image-bytes", 30))
    asyncio.run(store.set_json("bot:state:reminder_schedule:1", {"user_id": 1, "chat_id": 2}, 30))
    asyncio.run(store.set_json("bot:state:reminder_schedule:2", {"user_id": 2, "chat_id": 3}, 30))

    assert asyncio.run(store.get_bytes("api:bytes:/banner")) == b"image-bytes"

    scanned = asyncio.run(store.scan_json("bot:state:reminder_schedule:"))
    assert scanned == {
        "bot:state:reminder_schedule:1": {"user_id": 1, "chat_id": 2},
        "bot:state:reminder_schedule:2": {"user_id": 2, "chat_id": 3},
    }
