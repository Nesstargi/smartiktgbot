from backend.core.deps import PERMISSION_MANAGE_PRODUCTS


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_and_me_return_roles_and_permissions(client, create_user):
    user = create_user(
        email="manager@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )

    login_response = client.post(
        "/admin/auth/login",
        json={"email": "Manager@Example.com", "password": user["password"]},
    )

    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["user"]["email"] == user["email"]
    assert payload["user"]["roles"] == ["admin"]
    assert payload["user"]["permissions"] == [PERMISSION_MANAGE_PRODUCTS]

    me_response = client.get(
        "/admin/auth/me",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
    )

    assert me_response.status_code == 200
    assert me_response.json() == payload["user"]


def test_login_rate_limit_blocks_after_repeated_failures(client):
    for _ in range(5):
        response = client.post(
            "/admin/auth/login",
            json={"email": "missing@example.com", "password": "wrong-pass"},
        )
        assert response.status_code == 401

    blocked = client.post(
        "/admin/auth/login",
        json={"email": "missing@example.com", "password": "wrong-pass"},
    )

    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Too many login attempts. Try again later."
