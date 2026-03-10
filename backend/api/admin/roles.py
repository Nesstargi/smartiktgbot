from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.deps import require_super_admin
from backend.database import get_db
from backend.models.role import Role

router = APIRouter()


@router.get("/")
def list_roles(
    db: Session = Depends(get_db),
    admin=Depends(require_super_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [{"id": r.id, "name": r.name} for r in roles]
