from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.deps import PERMISSION_MANAGE_SUBCATEGORIES, require_permission
from backend.database import get_db
from backend.schemas.subcategory import SubCategoryCreate, SubCategoryOut, SubCategoryUpdate
from backend.services.subcategory_service import SubCategoryService

router = APIRouter()


@router.post("/", response_model=SubCategoryOut)
def create_subcategory(
    data: SubCategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_SUBCATEGORIES)),
):
    return SubCategoryService.create(db, data)


@router.get("/", response_model=list[SubCategoryOut])
def list_subcategories(
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_SUBCATEGORIES)),
):
    return SubCategoryService.list(db)


@router.put("/{subcategory_id}", response_model=SubCategoryOut)
def update_subcategory(
    subcategory_id: int,
    data: SubCategoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_SUBCATEGORIES)),
):
    subcategory = SubCategoryService.update(db, subcategory_id, data)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return subcategory


@router.delete("/{subcategory_id}")
def delete_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_SUBCATEGORIES)),
):
    ok = SubCategoryService.delete(db, subcategory_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return {"status": "deleted"}
