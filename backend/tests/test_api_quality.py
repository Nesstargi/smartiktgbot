from backend.core.deps import (
    PERMISSION_MANAGE_CATEGORIES,
    PERMISSION_MANAGE_PRODUCTS,
    PERMISSION_MANAGE_SUBCATEGORIES,
)


def test_public_subcategories_returns_404_for_missing_category(client):
    response = client.get("/api/subcategories/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_public_products_returns_404_for_missing_subcategory(client):
    response = client.get("/api/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Subcategory not found"


def test_category_create_rejects_duplicate_name_case_insensitively(
    client,
    create_user,
    auth_headers,
):
    admin = create_user(
        email="dup-category@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_CATEGORIES],
    )
    headers = auth_headers(admin["email"], admin["password"])

    first = client.post("/admin/categories/", headers=headers, json={"name": " Phones "})
    duplicate = client.post("/admin/categories/", headers=headers, json={"name": "phones"})

    assert first.status_code == 200
    assert first.json()["name"] == "Phones"
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Category with this name already exists"


def test_subcategory_create_requires_existing_category(
    client,
    create_user,
    auth_headers,
):
    admin = create_user(
        email="subcat-admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_SUBCATEGORIES],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/subcategories/",
        headers=headers,
        json={"name": "Android", "category_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_subcategory_create_rejects_duplicate_name_in_same_category(
    client,
    create_user,
    create_catalog,
    auth_headers,
):
    admin = create_user(
        email="subcat-dup@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_SUBCATEGORIES],
    )
    catalog = create_catalog(category_name="Phones", subcategory_name="Android")
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/subcategories/",
        headers=headers,
        json={"name": " android ", "category_id": catalog["category_id"]},
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Subcategory with this name already exists in this category"
    )


def test_product_create_requires_existing_subcategory(
    client,
    create_user,
    auth_headers,
):
    admin = create_user(
        email="product-admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.post(
        "/admin/products/",
        headers=headers,
        json={"name": "Galaxy A15", "subcategory_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Subcategory not found"


def test_product_create_rejects_duplicate_name_in_same_subcategory(
    client,
    create_user,
    create_catalog,
    auth_headers,
):
    admin = create_user(
        email="product-dup@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_PRODUCTS],
    )
    catalog = create_catalog()
    headers = auth_headers(admin["email"], admin["password"])

    first = client.post(
        "/admin/products/",
        headers=headers,
        json={"name": " Galaxy A15 ", "subcategory_id": catalog["subcategory_id"]},
    )
    duplicate = client.post(
        "/admin/products/",
        headers=headers,
        json={"name": "galaxy a15", "subcategory_id": catalog["subcategory_id"]},
    )

    assert first.status_code == 200
    assert first.json()["name"] == "Galaxy A15"
    assert duplicate.status_code == 409
    assert (
        duplicate.json()["detail"]
        == "Product with this name already exists in this subcategory"
    )


def test_dashboard_stats_returns_typed_counts(
    client,
    create_user,
    create_catalog,
    auth_headers,
):
    admin = create_user(
        email="dashboard-admin@example.com",
        password="secret123",
        roles=["admin"],
    )
    create_catalog()
    headers = auth_headers(admin["email"], admin["password"])

    response = client.get("/admin/dashboard/stats", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "products": 0,
        "categories": 1,
        "subcategories": 1,
        "promotions": 0,
        "leads": 0,
    }
