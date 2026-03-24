import backend.api.public.bot_admin as bot_admin_api
from backend.config import BOT_API_TOKEN
from backend.models.bot_subscriber import BotSubscriber
from backend.models.lead import Lead


def test_bot_admin_overview_returns_recent_leads_and_user_count(client, db_session):
    db_session.add_all(
        [
            BotSubscriber(chat_id="1001", telegram_user_id="1001"),
            BotSubscriber(chat_id="1002", telegram_user_id="1002"),
            Lead(name="Old", phone="+79990000001", product="A"),
            Lead(name="New", phone="+79990000002", product="B"),
        ]
    )
    db_session.commit()

    response = client.get(
        "/api/bot-admin/overview?limit=1",
        headers={"X-Bot-Token": BOT_API_TOKEN} if BOT_API_TOKEN else None,
    )

    assert response.status_code == 200
    assert response.json()["bot_users"] == 2
    assert response.json()["leads_total"] == 2
    assert len(response.json()["recent_leads"]) == 1
    assert response.json()["recent_leads"][0]["name"] == "New"


def test_bot_admin_overview_requires_bot_token_when_configured(client, monkeypatch):
    monkeypatch.setattr(bot_admin_api, "BOT_API_TOKEN", "secret-token")

    response = client.get("/api/bot-admin/overview")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
