import backend.api.public.leads as public_leads_api
from backend.config import BOT_API_TOKEN
from backend.models.bot_subscriber import BotSubscriber
from backend.models.lead import Lead


def test_bot_subscriber_register_creates_and_updates_record(client, db_session):
    first = client.post(
        "/api/bot-subscribers/register",
        headers={"X-Bot-Token": BOT_API_TOKEN} if BOT_API_TOKEN else None,
        json={
            "chat_id": 123456,
            "telegram_user_id": 123456,
            "username": "first_user",
            "full_name": "First User",
        },
    )

    assert first.status_code == 200
    assert first.json() == {"status": "ok"}

    created = db_session.query(BotSubscriber).filter(BotSubscriber.chat_id == "123456").first()
    assert created is not None
    assert created.username == "first_user"
    assert created.full_name == "First User"

    second = client.post(
        "/api/bot-subscribers/register",
        headers={"X-Bot-Token": BOT_API_TOKEN} if BOT_API_TOKEN else None,
        json={
            "chat_id": "123456",
            "telegram_user_id": "123456",
            "username": "updated_user",
            "full_name": "Updated User",
        },
    )

    assert second.status_code == 200
    db_session.expire_all()
    assert db_session.query(BotSubscriber).count() == 1

    updated = db_session.query(BotSubscriber).filter(BotSubscriber.chat_id == "123456").first()
    assert updated is not None
    assert updated.username == "updated_user"
    assert updated.full_name == "Updated User"


def test_public_create_lead_also_registers_subscriber(client, db_session):
    response = client.post(
        "/api/leads",
        json={
            "name": "Ivan",
            "phone": "+79990000001",
            "telegram_id": 777,
            "product": "Consultation",
        },
    )

    assert response.status_code == 200

    subscriber = db_session.query(BotSubscriber).filter(BotSubscriber.chat_id == "777").first()
    assert subscriber is not None
    assert subscriber.telegram_user_id == "777"
    assert subscriber.full_name == "Ivan"


def test_public_create_lead_still_succeeds_when_subscriber_sync_fails(
    client,
    db_session,
    monkeypatch,
):
    def fail_register(*args, **kwargs):
        raise RuntimeError("subscriber sync is unavailable")

    monkeypatch.setattr(public_leads_api.BotSubscriberService, "register", fail_register)

    response = client.post(
        "/api/leads",
        json={
            "name": "Ivan",
            "phone": "+79990000001",
            "telegram_id": 777,
            "product": "Consultation",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    lead = db_session.query(Lead).one()
    assert lead.name == "Ivan"
    assert lead.telegram_id == "777"
