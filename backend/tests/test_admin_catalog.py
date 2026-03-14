from backend.core.deps import (
    PERMISSION_MANAGE_CATEGORIES,
    PERMISSION_MANAGE_SUBCATEGORIES,
)
from backend.models.category import Category
from backend.models.subcategory import SubCategory


def test_category_routes_require_manage_categories_permission(
    client,
    create_user,
    auth_headers,
):
    admin = create_user(
        email="catalog-viewer@example.com",
        password="secret123",
        roles=["admin"],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/categories/",
        headers=headers,
        json={"name": "Phones"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_admin_can_crud_categories_and_subcategories(
    client,
    create_user,
    auth_headers,
    db_session,
):
    admin = create_user(
        email="catalog-admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[
            PERMISSION_MANAGE_CATEGORIES,
            PERMISSION_MANAGE_SUBCATEGORIES,
        ],
    )
    headers = auth_headers(admin["email"], admin["password"])

    create_category_response = client.post(
        "/admin/categories/",
        headers=headers,
        json={"name": "Phones"},
    )

    assert create_category_response.status_code == 200
    category = create_category_response.json()
    assert category["name"] == "Phones"

    list_categories_response = client.get("/admin/categories/", headers=headers)
    assert list_categories_response.status_code == 200
    assert list_categories_response.json() == [category]

    update_category_response = client.put(
        f"/admin/categories/{category['id']}",
        headers=headers,
        json={"name": "Smartphones"},
    )

    assert update_category_response.status_code == 200
    assert update_category_response.json()["name"] == "Smartphones"

    create_subcategory_response = client.post(
        "/admin/subcategories/",
        headers=headers,
        json={
            "name": "Android",
            "category_id": category["id"],
            "image_url": "/media/android.png",
        },
    )

    assert create_subcategory_response.status_code == 200
    subcategory = create_subcategory_response.json()
    assert subcategory["name"] == "Android"
    assert subcategory["category_id"] == category["id"]

    list_subcategories_response = client.get("/admin/subcategories/", headers=headers)
    assert list_subcategories_response.status_code == 200
    assert len(list_subcategories_response.json()) == 1

    update_subcategory_response = client.put(
        f"/admin/subcategories/{subcategory['id']}",
        headers=headers,
        json={"name": "Android Updated", "image_url": "/media/android-2.png"},
    )

    assert update_subcategory_response.status_code == 200
    updated_subcategory = update_subcategory_response.json()
    assert updated_subcategory["name"] == "Android Updated"
    assert updated_subcategory["image_url"] == "/media/android-2.png"

    delete_subcategory_response = client.delete(
        f"/admin/subcategories/{subcategory['id']}",
        headers=headers,
    )

    assert delete_subcategory_response.status_code == 200
    assert delete_subcategory_response.json() == {"status": "deleted"}
    assert (
        db_session.query(SubCategory)
        .filter(SubCategory.id == subcategory["id"])
        .first()
        is None
    )

    delete_category_response = client.delete(
        f"/admin/categories/{category['id']}",
        headers=headers,
    )

    assert delete_category_response.status_code == 200
    assert delete_category_response.json() == {"status": "deleted"}
    assert db_session.query(Category).filter(Category.id == category["id"]).first() is None
