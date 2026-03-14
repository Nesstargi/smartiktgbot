from backend.core.deps import PERMISSION_MANAGE_PRODUCTS
from backend.models.product import Product


def test_product_routes_require_manage_products_permission(
    client,
    create_user,
    create_catalog,
    auth_headers,
):
    user = create_user(
        email="limited@example.com",
        password="secret123",
        roles=["admin"],
    )
    catalog = create_catalog()
    headers = auth_headers(user["email"], user["password"])

    response = client.post(
        "/admin/products/",
        headers=headers,
        json={
            "name": "Phone",
            "description": "128GB",
            "subcategory_id": catalog["subcategory_id"],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_admin_can_crud_products(
    client,
    create_user,
    create_catalog,
    auth_headers,
    db_session,
):
    user = create_user(
        email="products@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )
    catalog = create_catalog()
    headers = auth_headers(user["email"], user["password"])

    create_response = client.post(
        "/admin/products/",
        headers=headers,
        json={
            "name": "Galaxy A15",
            "description": "128GB",
            "subcategory_id": catalog["subcategory_id"],
            "image_file_id": "file-1",
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["name"] == "Galaxy A15"
    assert created["image_file_id"] == "file-1"

    list_response = client.get("/admin/products/", headers=headers)

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["id"] == created["id"]

    update_response = client.put(
        f"/admin/products/{created['id']}",
        headers=headers,
        json={
            "name": "Galaxy A15 Updated",
            "description": "256GB",
            "image_file_id": "file-2",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Galaxy A15 Updated"
    assert updated["description"] == "256GB"
    assert updated["image_file_id"] == "file-2"

    delete_response = client.delete(
        f"/admin/products/{created['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {"status": "deleted"}
    assert db_session.query(Product).filter(Product.id == created["id"]).first() is None
