from backend.core.deps import PERMISSION_MANAGE_NOTIFICATIONS
from backend.models.lead import Lead
from backend.services.notification_service import NotificationService


def test_notifications_require_permission(client, create_user, auth_headers):
    admin = create_user(
        email="notify-limited@example.com",
        password="secret123",
        roles=["admin"],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/notifications/broadcast",
        headers=headers,
        json={"title": "Promo", "message": "Hello"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_notifications_broadcast_uses_distinct_non_empty_chat_ids(
    client,
    create_user,
    auth_headers,
    db_session,
    monkeypatch,
):
    admin = create_user(
        email="notify-admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_NOTIFICATIONS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    db_session.add_all(
        [
            Lead(phone="+10000000001", telegram_id="123"),
            Lead(phone="+10000000002", telegram_id="123"),
            Lead(phone="+10000000003", telegram_id="456"),
            Lead(phone="+10000000004", telegram_id=None),
            Lead(phone="+10000000005", telegram_id=""),
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
        return {"total": len(chat_ids), "success": len(chat_ids), "failed": 0}

    monkeypatch.setattr(
        NotificationService,
        "send_broadcast",
        staticmethod(fake_send_broadcast),
    )

    response = client.post(
        "/admin/notifications/broadcast",
        headers=headers,
        json={
            "title": "New promo",
            "message": "Check this out",
            "image_url": "/media/banner.jpg",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"total": 2, "success": 2, "failed": 0}
    assert set(captured["chat_ids"]) == {"123", "456"}
    assert captured["title"] == "New promo"
    assert captured["message"] == "Check this out"
    assert captured["image_url"] == "/media/banner.jpg"
    assert captured["image_file_id"] is None
