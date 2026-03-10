from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.deps import PERMISSION_MANAGE_LEADS, require_permission
from backend.database import get_db
from backend.models.lead import Lead
from backend.schemas.lead import LeadOut

router = APIRouter()


@router.get("/", response_model=list[LeadOut])
def list_leads(
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_LEADS)),
):
    return db.query(Lead).order_by(Lead.id.desc()).all()


@router.delete("/{lead_id}")
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
