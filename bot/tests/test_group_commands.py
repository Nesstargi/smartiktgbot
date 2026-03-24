import asyncio
from types import SimpleNamespace

from bot.handlers import menu as menu_handler


class FakeBot:
    def __init__(self, status="administrator"):
        self.status = status

    async def get_chat_member(self, chat_id, user_id):
        return SimpleNamespace(status=self.status)


class FakeMessage:
    def __init__(self, text, *, chat_type="group", status="administrator"):
        self.text = text
        self.chat = SimpleNamespace(id=-100500, type=chat_type)
        self.from_user = SimpleNamespace(id=42, username="boss", full_name="Boss User")
        self.bot = FakeBot(status=status)
        self.answers = []

    async def answer(self, text, reply_markup=None):
        self.answers.append({"text": text, "reply_markup": reply_markup})


def test_group_start_shows_available_commands(monkeypatch):
    monkeypatch.setattr(menu_handler, "schedule_bot_subscriber_sync", lambda **kwargs: None)

    message = FakeMessage("/start")

    asyncio.run(menu_handler.start(message))

    assert "/stats" in message.answers[0]["text"]
    assert "/orders" in message.answers[0]["text"]
    assert message.answers[0]["reply_markup"] is None


def test_group_users_returns_bot_user_count(monkeypatch):
    monkeypatch.setattr(menu_handler, "schedule_bot_subscriber_sync", lambda **kwargs: None)

    async def fake_overview(limit=10):
        return {"bot_users": 17, "leads_total": 4, "recent_leads": []}

    monkeypatch.setattr(menu_handler, "get_bot_admin_overview", fake_overview)
    message = FakeMessage("/users")

    asyncio.run(menu_handler.group_users(message))

    assert message.answers == [{"text": "Пользователей бота: 17", "reply_markup": None}]


def test_group_orders_formats_recent_leads(monkeypatch):
    monkeypatch.setattr(menu_handler, "schedule_bot_subscriber_sync", lambda **kwargs: None)

    async def fake_overview(limit=10):
        return {
            "bot_users": 17,
            "leads_total": 2,
            "recent_leads": [
                {
                    "id": 2,
                    "name": "Иван",
                    "phone": "+79990000002",
                    "product": "Консультация",
                    "created_at": "2026-03-25T10:15:00+00:00",
                },
                {
                    "id": 1,
                    "name": "Мария",
                    "phone": "+79990000001",
                    "product": "Каталог",
                    "created_at": "2026-03-25T09:00:00+00:00",
                },
            ],
        }

    monkeypatch.setattr(menu_handler, "get_bot_admin_overview", fake_overview)
    message = FakeMessage("/orders")

    asyncio.run(menu_handler.group_orders(message))

    text = message.answers[0]["text"]
    assert "Последние заявки: 2 из 2" in text
    assert "Иван" in text
    assert "+79990000002" in text


def test_group_orders_rejects_invalid_limit(monkeypatch):
    monkeypatch.setattr(menu_handler, "schedule_bot_subscriber_sync", lambda **kwargs: None)
    message = FakeMessage("/orders 50")

    asyncio.run(menu_handler.group_orders(message))

    assert "Использование: /orders" in message.answers[0]["text"]
