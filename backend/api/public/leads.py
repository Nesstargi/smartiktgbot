from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Lead
from backend.schemas.lead import LeadCreate

router = APIRouter()


@router.post("/leads")
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        name=data.name,
        phone=data.phone,
        telegram_id=str(data.telegram_id) if data.telegram_id is not None else None,
        product=str(data.product) if data.product is not None else None,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"status": "ok"}
