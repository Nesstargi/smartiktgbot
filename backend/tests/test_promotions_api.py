from backend.core.deps import PERMISSION_MANAGE_PROMOTIONS
from backend.models.promotion import Promotion
from backend.services.notification_service import NotificationService


def test_public_promotions_returns_only_active_items_in_desc_order(client, db_session):
    db_session.add_all(
        [
            Promotion(title="Old active", is_active=True),
            Promotion(title="Hidden", is_active=False),
            Promotion(title="New active", is_active=True),
        ]
    )
    db_session.commit()

    response = client.get("/api/promotions")

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["New active", "Old active"]


def test_promotion_create_rejects_duplicate_title_case_insensitively(
    client,
    create_user,
    auth_headers,
):
    admin = create_user(
        email="promo-admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PROMOTIONS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    first = client.post(
        "/admin/promotions/",
        headers=headers,
        json={"title": " Spring Sale ", "description": "One", "is_active": True},
    )
    duplicate = client.post(
        "/admin/promotions/",
        headers=headers,
        json={"title": "spring sale", "description": "Two", "is_active": True},
    )

    assert first.status_code == 200
    assert first.json()["title"] == "Spring Sale"
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Promotion with this title already exists"


def test_promotion_send_to_all_requires_notification_configuration(
    client,
    create_user,
    auth_headers,
    db_session,
    monkeypatch,
):
    admin = create_user(
        email="promo-broadcast@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PROMOTIONS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    monkeypatch.setattr(
        NotificationService,
        "is_configured",
        staticmethod(lambda: False),
    )

    response = client.post(
        "/admin/promotions/",
        headers=headers,
        json={
            "title": "Broadcast promo",
            "description": "Desc",
            "is_active": True,
            "send_to_all": True,
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Notification service is not configured"
    assert db_session.query(Promotion).count() == 0


def test_promotion_send_to_all_creates_item_and_broadcasts(
    client,
    create_user,
    auth_headers,
    db_session,
    monkeypatch,
):
    admin = create_user(
        email="promo-send@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PROMOTIONS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    from backend.models.lead import Lead

    db_session.add_all(
        [
            Lead(phone="+10000000001", telegram_id="111"),
            Lead(phone="+10000000002", telegram_id="111"),
            Lead(phone="+10000000003", telegram_id="222"),
        ]
    )
    db_session.commit()

    captured = {}

    async def fake_send_broadcast(chat_ids, title, message, image_url=None, image_file_id=None):
        captured["chat_ids"] = chat_ids
        captured["title"] = title
        captured["message"] = message
        captured["image_url"] = image_url
        captured["image_file_id"] = image_file_id
        return {"total": 2, "success": 2, "failed": 0}

    monkeypatch.setattr(
        NotificationService,
        "is_configured",
        staticmethod(lambda: True),
    )
    monkeypatch.setattr(
        NotificationService,
        "send_broadcast",
        staticmethod(fake_send_broadcast),
    )

    response = client.post(
        "/admin/promotions/",
        headers=headers,
        json={
            "title": "Weekend Promo",
            "description": "Big discount",
            "image_url": "/media/banner.jpg",
            "is_active": True,
            "send_to_all": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Weekend Promo"
    assert set(captured["chat_ids"]) == {"111", "222"}
    assert captured["title"] == "Новая акция: Weekend Promo"
    assert captured["message"] == "Big discount"
    assert captured["image_url"] == "/media/banner.jpg"


def test_promotion_update_rejects_duplicate_title(
    client,
    create_user,
    auth_headers,
    db_session,
):
    admin = create_user(
        email="promo-edit@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PROMOTIONS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    db_session.add_all(
        [
            Promotion(title="Promo One", is_active=True),
            Promotion(title="Promo Two", is_active=True),
        ]
    )
    db_session.commit()
    promotions = db_session.query(Promotion).order_by(Promotion.id.asc()).all()

    response = client.put(
        f"/admin/promotions/{promotions[1].id}",
        headers=headers,
        json={"title": " promo one "},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Promotion with this title already exists"
