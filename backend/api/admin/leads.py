from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.api.utils import normalize_search_query, paginate_query
from backend.core.deps import PERMISSION_MANAGE_LEADS, require_permission
from backend.database import get_db
from backend.models.lead import Lead
from backend.schemas.common import StatusOut
from backend.schemas.lead import LeadOut

router = APIRouter()


@router.get("/", response_model=list[LeadOut])
def list_leads(
    response: Response,
    q: str | None = Query(default=None, max_length=200),
    limit: int | None = Query(default=None, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_LEADS)),
):
    query = db.query(Lead)
    term = normalize_search_query(q)
    if term:
        pattern = f"%{term}%"
        query = query.filter(
            or_(
                Lead.name.ilike(pattern),
                Lead.phone.ilike(pattern),
                Lead.telegram_id.ilike(pattern),
                Lead.product.ilike(pattern),
            )
        )

    return paginate_query(
        query.order_by(Lead.created_at.desc(), Lead.id.desc()),
        response,
        limit=limit,
        offset=offset,
    )


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_LEADS)),
):
    item = db.query(Lead).filter(Lead.id == lead_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Lead not found")
    return item


@router.delete("/{lead_id}", response_model=StatusOut)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_LEADS)),
):
    item = db.query(Lead).filter(Lead.id == lead_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(item)
    db.commit()
    return {"status": "deleted"}
