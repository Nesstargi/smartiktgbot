import asyncio
from types import SimpleNamespace

from bot.handlers import catalog_promotions


class FakeMessage:
    def __init__(self):
        self.chat = SimpleNamespace(id=123, type="private")
        self.from_user = SimpleNamespace(id=456, username="tester", full_name="Test User")
        self.answers = []

    async def answer(self, text, parse_mode=None):
        self.answers.append({"text": text, "parse_mode": parse_mode})


class FakeSentMessage:
    def __init__(self, file_id: str):
        self.photo = [SimpleNamespace(file_id=file_id)]


def test_show_promotions_falls_back_to_image_url_when_file_id_is_stale(monkeypatch):
    promotions = [
        {
            "id": 10,
            "title": "Весенняя акция",
            "description": "Скидка 15%",
            "image_url": "/media/promo.jpg",
            "image_file_id": "stale-file-id",
        }
    ]
    send_calls = []
    remembered = []
    updated = []

    monkeypatch.setattr(catalog_promotions, "schedule_bot_subscriber_sync", lambda **kwargs: None)

    async def fake_clear_consultation_waiting(_user_id):
        return None

    async def fake_get_promotions(force_refresh=False):
        assert force_refresh is True
        return promotions

    async def fake_photo_payload(photo_ref):
        if photo_ref == "stale-file-id":
            return "stale-photo"
        if photo_ref == "/media/promo.jpg":
            return "fresh-photo"
        return None

    async def fake_send_photo_with_fallback(message, photo, **kwargs):
        send_calls.append({"photo": photo, "kwargs": kwargs})
        if photo == "stale-photo":
            return None
        if photo == "fresh-photo":
            return FakeSentMessage("new-file-id")
        return None

    async def fake_remember_sent_photo(image_url, sent):
        remembered.append((image_url, sent.photo[-1].file_id))

    async def fake_update_promotion_file_id(promotion_id, image_file_id):
        updated.append((promotion_id, image_file_id))
        return {"id": promotion_id, "image_file_id": image_file_id}

    monkeypatch.setattr(catalog_promotions, "clear_consultation_waiting", fake_clear_consultation_waiting)
    monkeypatch.setattr(catalog_promotions, "get_promotions", fake_get_promotions)
    monkeypatch.setattr(catalog_promotions, "photo_payload", fake_photo_payload)
    monkeypatch.setattr(catalog_promotions, "send_photo_with_fallback", fake_send_photo_with_fallback)
    monkeypatch.setattr(catalog_promotions, "remember_sent_photo", fake_remember_sent_photo)
    monkeypatch.setattr(catalog_promotions, "update_promotion_file_id", fake_update_promotion_file_id)

    message = FakeMessage()

    asyncio.run(catalog_promotions.show_promotions(message))

    assert [call["photo"] for call in send_calls] == ["stale-photo", "stale-photo", "fresh-photo"]
    assert remembered == [("/media/promo.jpg", "new-file-id")]
    assert updated == [(10, "new-file-id")]
    assert message.answers == [{"text": "🔥 *Акции*", "parse_mode": "Markdown"}]
