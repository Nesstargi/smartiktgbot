from backend.core.deps import (
    PERMISSION_MANAGE_CATEGORIES,
    PERMISSION_MANAGE_PRODUCTS,
)
from backend.models.user import User


def test_non_super_admin_cannot_access_user_management(
    client,
    create_user,
    auth_headers,
):
    admin = create_user(
        email="admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    users_response = client.get("/admin/users/", headers=headers)
    roles_response = client.get("/admin/roles/", headers=headers)

    assert users_response.status_code == 403
    assert users_response.json()["detail"] == "Super admin only"
    assert roles_response.status_code == 403
    assert roles_response.json()["detail"] == "Super admin only"


def test_super_admin_can_manage_users_and_roles(
    client,
    create_super_admin,
    auth_headers,
    db_session,
):
    super_admin = create_super_admin()
    headers = auth_headers(super_admin["email"], super_admin["password"])

    permissions_response = client.get("/admin/users/permissions", headers=headers)
    assert permissions_response.status_code == 200
    assert PERMISSION_MANAGE_PRODUCTS in permissions_response.json()["permissions"]

    create_response = client.post(
        "/admin/users/",
        headers=headers,
        json={
            "email": "manager@example.com",
            "password": "strongpass",
            "is_super_admin": False,
            "permissions": [PERMISSION_MANAGE_PRODUCTS],
        },
    )

    assert create_response.status_code == 200
    created_user = create_response.json()
    assert created_user["email"] == "manager@example.com"
    assert created_user["roles"] == ["admin"]
    assert created_user["permissions"] == [PERMISSION_MANAGE_PRODUCTS]

    list_response = client.get("/admin/users/", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    update_permissions_response = client.put(
        f"/admin/users/{created_user['id']}/permissions",
        headers=headers,
        json={"permissions": [PERMISSION_MANAGE_CATEGORIES]},
    )

    assert update_permissions_response.status_code == 200
    assert update_permissions_response.json()["permissions"] == [
        PERMISSION_MANAGE_CATEGORIES
    ]

    promote_response = client.put(
        f"/admin/users/{created_user['id']}/role",
        headers=headers,
        json={"is_super_admin": True},
    )

    assert promote_response.status_code == 200
    assert sorted(promote_response.json()["roles"]) == ["admin", "super_admin"]

    roles_response = client.get("/admin/roles/", headers=headers)
    assert roles_response.status_code == 200
    assert {item["name"] for item in roles_response.json()} >= {"admin", "super_admin"}

    delete_response = client.delete(
        f"/admin/users/{created_user['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {"status": "deleted"}
    assert (
        db_session.query(User).filter(User.email == "manager@example.com").first()
        is None
    )


def test_super_admin_user_creation_rejects_unknown_permissions(
    client,
    create_super_admin,
    auth_headers,
):
    super_admin = create_super_admin(email="boss@example.com")
    headers = auth_headers(super_admin["email"], super_admin["password"])

    response = client.post(
        "/admin/users/",
        headers=headers,
        json={
            "email": "broken@example.com",
            "password": "strongpass",
            "is_super_admin": False,
            "permissions": ["unknown_permission"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown permissions: unknown_permission"
