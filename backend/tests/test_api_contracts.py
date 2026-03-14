from backend.core.deps import (
    PERMISSION_MANAGE_CATEGORIES,
    PERMISSION_MANAGE_LEADS,
    PERMISSION_MANAGE_PRODUCTS,
    PERMISSION_MANAGE_PROMOTIONS,
    PERMISSION_MANAGE_SUBCATEGORIES,
)
from backend.models.category import Category
from backend.models.lead import Lead
from backend.models.product import Product
from backend.models.promotion import Promotion
from backend.models.subcategory import SubCategory


def test_http_errors_include_code_and_path(client, create_user, auth_headers):
    admin = create_user(
        email="limited@example.com",
        password="secret123",
        roles=["admin"],
    )
    headers = auth_headers(admin["email"], admin["password"])

    response = client.get("/admin/users/", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Super admin only"
    assert response.json()["code"] == "forbidden"
    assert response.json()["path"] == "/admin/users/"


def test_validation_errors_include_code_and_errors(
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
            "email": "new@example.com",
            "password": "short",
            "is_super_admin": False,
            "permissions": [],
        },
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert response.json()["path"] == "/admin/users/"
    assert response.json()["detail"] == response.json()["errors"]
    assert any(item["loc"][-1] == "password" for item in response.json()["errors"])


def test_not_found_errors_use_same_shape(client):
    response = client.get("/missing-route")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Not Found",
        "code": "not_found",
        "path": "/missing-route",
    }


def test_admin_users_list_supports_query_pagination_and_total_count(
    client,
    create_super_admin,
    create_user,
    auth_headers,
):
    super_admin = create_super_admin(email="root@example.com")
    create_user(email="manager.one@example.com", roles=["admin"])
    create_user(email="manager.two@example.com", roles=["admin"])
    create_user(email="support@example.com", roles=["admin"])
    headers = auth_headers(super_admin["email"], super_admin["password"])

    response = client.get(
        "/admin/users/",
        headers=headers,
        params={"q": "manager", "limit": 1, "offset": 0},
    )

    assert response.status_code == 200
    assert response.headers["x-total-count"] == "2"
    assert len(response.json()) == 1
    assert response.json()[0]["email"].startswith("manager.")


def test_admin_catalog_lists_support_filters_and_total_count(
    client,
    create_user,
    auth_headers,
    db_session,
):
    admin = create_user(
        email="catalog@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[
            PERMISSION_MANAGE_CATEGORIES,
            PERMISSION_MANAGE_SUBCATEGORIES,
            PERMISSION_MANAGE_PRODUCTS,
        ],
    )
    headers = auth_headers(admin["email"], admin["password"])

    phones = Category(name="Phones")
    laptops = Category(name="Laptops")
    db_session.add_all([phones, laptops])
    db_session.commit()
    db_session.refresh(phones)
    db_session.refresh(laptops)

    android = SubCategory(name="Android", category_id=phones.id)
    ios = SubCategory(name="iOS", category_id=phones.id)
    ultrabooks = SubCategory(name="Ultrabooks", category_id=laptops.id)
    db_session.add_all([android, ios, ultrabooks])
    db_session.commit()
    db_session.refresh(android)
    db_session.refresh(ios)
    db_session.refresh(ultrabooks)

    db_session.add_all(
        [
            Product(
                name="Galaxy A55",
                description="Midrange Android",
                subcategory_id=android.id,
            ),
            Product(
                name="iPhone 15",
                description="iOS flagship",
                subcategory_id=ios.id,
            ),
            Product(
                name="Zenbook 14",
                description="Ultrabook laptop",
                subcategory_id=ultrabooks.id,
            ),
        ]
    )
    db_session.commit()

    categories_response = client.get(
        "/admin/categories/",
        headers=headers,
        params={"q": "phone"},
    )
    assert categories_response.status_code == 200
    assert categories_response.headers["x-total-count"] == "1"
    assert [item["name"] for item in categories_response.json()] == ["Phones"]

    subcategories_response = client.get(
        "/admin/subcategories/",
        headers=headers,
        params={"category_id": phones.id, "limit": 1},
    )
    assert subcategories_response.status_code == 200
    assert subcategories_response.headers["x-total-count"] == "2"
    assert len(subcategories_response.json()) == 1
    assert subcategories_response.json()[0]["category_id"] == phones.id

    products_response = client.get(
        "/admin/products/",
        headers=headers,
        params={"category_id": phones.id, "q": "android"},
    )
    assert products_response.status_code == 200
    assert products_response.headers["x-total-count"] == "1"
    assert [item["name"] for item in products_response.json()] == ["Galaxy A55"]


def test_admin_promotions_and_leads_lists_support_filters_and_total_count(
    client,
    create_user,
    auth_headers,
    db_session,
):
    admin = create_user(
        email="crm@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[
            PERMISSION_MANAGE_PROMOTIONS,
            PERMISSION_MANAGE_LEADS,
        ],
    )
    headers = auth_headers(admin["email"], admin["password"])

    db_session.add_all(
        [
            Promotion(
                title="Spring Sale",
                description="Phones discount",
                is_active=True,
            ),
            Promotion(
                title="Laptop Week",
                description="Notebook discount",
                is_active=False,
            ),
            Promotion(
                title="Spring Bonus",
                description="Accessories",
                is_active=True,
            ),
        ]
    )
    db_session.add_all(
        [
            Lead(name="Ivan", phone="+79990000001", telegram_id="@ivan", product="Phone"),
            Lead(name="Anna", phone="+79990000002", telegram_id="@anna", product="Laptop"),
            Lead(name="Irina", phone="+79990000003", telegram_id="@iri", product="Phone"),
        ]
    )
    db_session.commit()

    promotions_response = client.get(
        "/admin/promotions/",
        headers=headers,
        params={"q": "spring", "is_active": "true", "limit": 1},
    )
    assert promotions_response.status_code == 200
    assert promotions_response.headers["x-total-count"] == "2"
    assert len(promotions_response.json()) == 1

    leads_response = client.get(
        "/admin/leads/",
        headers=headers,
        params={"q": "phone", "offset": 1, "limit": 1},
    )
    assert leads_response.status_code == 200
    assert leads_response.headers["x-total-count"] == "2"
    assert len(leads_response.json()) == 1
