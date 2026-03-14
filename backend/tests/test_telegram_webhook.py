from backend.api.public import telegram as telegram_api


def test_telegram_webhook_returns_404_when_mode_is_not_webhook(client, monkeypatch):
    monkeypatch.setattr(telegram_api, "is_webhook_mode", lambda: False)

    response = client.post(telegram_api.TELEGRAM_WEBHOOK_ROUTE, json={"update_id": 1})

    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook is not enabled"


def test_telegram_webhook_rejects_invalid_secret(client, monkeypatch):
    monkeypatch.setattr(telegram_api, "is_webhook_mode", lambda: True)
    monkeypatch.setattr(telegram_api, "webhook_secret_is_valid", lambda value: value == "good-secret")

    response = client.post(
        telegram_api.TELEGRAM_WEBHOOK_ROUTE,
        json={"update_id": 1},
        headers={"X-Telegram-Bot-Api-Secret-Token": "bad-secret"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid webhook secret"


def test_telegram_webhook_processes_update(client, monkeypatch):
    captured = {}

    async def fake_process_webhook_update(payload):
        captured["payload"] = payload

    monkeypatch.setattr(telegram_api, "is_webhook_mode", lambda: True)
    monkeypatch.setattr(telegram_api, "webhook_secret_is_valid", lambda value: value == "good-secret")
    monkeypatch.setattr(telegram_api, "process_webhook_update", fake_process_webhook_update)

    payload = {
        "update_id": 1001,
        "message": {
            "message_id": 1,
            "date": 1_700_000_000,
            "chat": {"id": 123, "type": "private"},
            "from": {"id": 123, "is_bot": False, "first_name": "Test"},
            "text": "/start",
        },
    }

    response = client.post(
        telegram_api.TELEGRAM_WEBHOOK_ROUTE,
        json=payload,
        headers={"X-Telegram-Bot-Api-Secret-Token": "good-secret"},
    )

    assert response.status_code == 200
    assert response.text == ""
    assert captured["payload"] == payload
