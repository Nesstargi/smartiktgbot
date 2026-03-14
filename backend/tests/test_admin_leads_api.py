from backend.core.deps import PERMISSION_MANAGE_LEADS
from backend.models.lead import Lead


def test_admin_leads_list_supports_search_and_get_by_id(
    client,
    create_user,
    auth_headers,
    db_session,
):
    admin = create_user(
        email="leads-admin@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_LEADS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    db_session.add_all(
        [
            Lead(name="Ivan", phone="+79990000001", telegram_id="111", product="iPhone"),
            Lead(name="Petr", phone="+79990000002", telegram_id="222", product="Galaxy"),
        ]
    )
    db_session.commit()
    leads = db_session.query(Lead).order_by(Lead.id.asc()).all()

    search_response = client.get("/admin/leads/?q=gal", headers=headers)
    get_response = client.get(f"/admin/leads/{leads[0].id}", headers=headers)

    assert search_response.status_code == 200
    assert len(search_response.json()) == 1
    assert search_response.json()[0]["product"] == "Galaxy"

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Ivan"
    assert get_response.json()["phone"] == "+79990000001"


def test_admin_leads_delete_and_missing_lead_behavior(
    client,
    create_user,
    auth_headers,
    db_session,
):
    admin = create_user(
        email="leads-delete@example.com",
        password="secret123",
        roles=["admin"],
        permissions=[PERMISSION_MANAGE_LEADS],
    )
    headers = auth_headers(admin["email"], admin["password"])

    lead = Lead(phone="+79990000003", product="Consultation")
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)

    delete_response = client.delete(f"/admin/leads/{lead.id}", headers=headers)
    missing_response = client.get("/admin/leads/999", headers=headers)

    assert delete_response.status_code == 200
    assert delete_response.json() == {"status": "deleted"}
    assert db_session.query(Lead).filter(Lead.id == lead.id).first() is None

    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Lead not found"
