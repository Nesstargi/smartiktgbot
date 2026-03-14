from io import BytesIO

from PIL import Image

from backend.core.deps import PERMISSION_MANAGE_BOT_SETTINGS, PERMISSION_MANAGE_PRODUCTS
from backend.models.bot_setting import BotSetting
from backend.schemas.bot_setting import (
    DEFAULT_ABOUT_MESSAGE,
    DEFAULT_CONSULTATION_CONTACT_PROMPT,
    DEFAULT_CONSULTATION_MESSAGE,
    DEFAULT_CONSULTATION_PHONE,
    DEFAULT_REMINDER,
)
from backend.services import media_services


def _png_bytes() -> bytes:
    image = Image.new("RGBA", (2, 2), (255, 0, 0, 255))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _large_png_bytes() -> bytes:
    image = Image.new("RGBA", (2600, 1800), (0, 128, 255, 180))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_public_bot_settings_returns_defaults_and_creates_row(client, db_session):
    response = client.get("/api/bot-settings")

    assert response.status_code == 200
    assert response.json() == {
        "start_message": "Welcome! Choose a menu option.",
        "abandoned_reminder_message": DEFAULT_REMINDER,
        "abandoned_reminder_delay_minutes": 30,
        "consultation_phone": DEFAULT_CONSULTATION_PHONE,
        "consultation_message": DEFAULT_CONSULTATION_MESSAGE,
        "consultation_contact_prompt": DEFAULT_CONSULTATION_CONTACT_PROMPT,
        "about_message": DEFAULT_ABOUT_MESSAGE,
    }
    assert db_session.query(BotSetting).count() == 1


def test_admin_bot_settings_require_permission(client, create_user, auth_headers):
    admin = create_user(
        email="settings-viewer@example.com",
        password="secret123",
        roles=["admin"],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.get("/admin/bot-settings/", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_admin_can_update_bot_settings_and_public_endpoint_sees_changes(
    client,
    create_user,
    auth_headers,
):
    admin = create_user(
        email="settings-admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_BOT_SETTINGS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    update_payload = {
        "start_message": "Hello from admin",
        "abandoned_reminder_message": "Please come back",
        "abandoned_reminder_delay_minutes": 45,
        "consultation_phone": "+7 (111) 111-11-11",
        "consultation_message": "Call us: {phone}",
        "consultation_contact_prompt": "Send your phone",
        "about_message": "About us updated",
    }

    update_response = client.put(
        "/admin/bot-settings/",
        headers=headers,
        json=update_payload,
    )

    assert update_response.status_code == 200
    assert update_response.json() == update_payload

    public_response = client.get("/api/bot-settings")

    assert public_response.status_code == 200
    assert public_response.json() == update_payload


def test_upload_rejects_invalid_extension(client, create_user, auth_headers, tmp_path, monkeypatch):
    monkeypatch.setattr(media_services, "MEDIA_DIR", tmp_path)

    admin = create_user(
        email="upload-admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/upload/file",
        headers=headers,
        files={"file": ("notes.txt", b"not-an-image", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Allowed image formats: png, jpg, jpeg, webp, jfif"
    assert list(tmp_path.iterdir()) == []


def test_upload_png_is_saved_as_jpg(
    client,
    create_user,
    auth_headers,
    tmp_path,
    monkeypatch,
):
    tmp_path.mkdir(exist_ok=True)
    monkeypatch.setattr(media_services, "MEDIA_DIR", tmp_path)

    admin = create_user(
        email="upload-editor@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/upload/file",
        headers=headers,
        files={"file": ("picture.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["filename"].endswith(".jpg")
    assert payload["url"] == f"/media/{payload['filename']}"

    saved_path = tmp_path / payload["filename"]
    assert saved_path.exists()
    assert saved_path.suffix == ".jpg"

    with Image.open(saved_path) as saved_image:
        assert saved_image.format == "JPEG"
        assert saved_image.mode == "RGB"
        assert max(saved_image.size) == 2


def test_upload_rejects_invalid_image_content(
    client,
    create_user,
    auth_headers,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(media_services, "MEDIA_DIR", tmp_path)

    admin = create_user(
        email="upload-invalid-content@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/upload/file",
        headers=headers,
        files={"file": ("broken.jpg", b"not-a-real-image", "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file"
    assert list(tmp_path.iterdir()) == []


def test_upload_large_png_is_resized_and_optimized(
    client,
    create_user,
    auth_headers,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(media_services, "MEDIA_DIR", tmp_path)

    admin = create_user(
        email="upload-large-image@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/upload/file",
        headers=headers,
        files={"file": ("large.png", _large_png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    saved_path = tmp_path / payload["filename"]
    assert saved_path.exists()
    assert saved_path.stat().st_size > 0

    with Image.open(saved_path) as saved_image:
        assert saved_image.format == "JPEG"
        assert saved_image.mode == "RGB"
        assert max(saved_image.size) == 1600


def test_upload_requires_one_of_catalog_permissions(client, create_user, auth_headers):
    admin = create_user(
        email="upload-limited@example.com",
        password="secret123",
        roles=["admin"],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/upload/file",
        headers=headers,
        files={"file": ("picture.jpg", b"jpeg", "image/jpeg")},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"
