from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.deps import PERMISSION_MANAGE_CATEGORIES, require_permission
from backend.database import get_db
from backend.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from backend.services.category_service import CategoryService

router = APIRouter()


@router.post("/", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_CATEGORIES)),
):
    return CategoryService.create(db, data)


@router.get("/", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_CATEGORIES)),
):
    return CategoryService.list(db)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_CATEGORIES)),
):
    category = CategoryService.update(db, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_CATEGORIES)),
):
    ok = CategoryService.delete(db, category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "deleted"}
