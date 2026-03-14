from backend.models.lead import Lead


def test_public_create_lead_persists_values(client, db_session):
    response = client.post(
        "/api/leads",
        json={
            "name": "Ivan",
            "phone": "+79990001122",
            "telegram_id": 123456,
            "product": 42,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    lead = db_session.query(Lead).one()
    assert lead.name == "Ivan"
    assert lead.phone == "+79990001122"
    assert lead.telegram_id == "123456"
    assert lead.product == "42"
    assert lead.created_at is not None


def test_public_create_lead_validates_phone_length(client):
    response = client.post(
        "/api/leads",
        json={
            "name": "Ivan",
            "phone": "1234",
        },
    )

    assert response.status_code == 422
