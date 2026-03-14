from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from backend.api.utils import normalize_search_query, paginate_query
from backend.core.deps import PERMISSION_MANAGE_CATEGORIES, require_permission
from backend.database import get_db
from backend.models.category import Category
from backend.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from backend.schemas.common import StatusOut
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
    response: Response,
    q: str | None = Query(default=None, max_length=200),
    limit: int | None = Query(default=None, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_CATEGORIES)),
):
    query = db.query(Category)
    term = normalize_search_query(q)
    if term:
        query = query.filter(Category.name.ilike(f"%{term}%"))

    return paginate_query(
        query.order_by(Category.id.asc()),
        response,
        limit=limit,
        offset=offset,
    )


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


@router.delete("/{category_id}", response_model=StatusOut)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_CATEGORIES)),
):
    ok = CategoryService.delete(db, category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "deleted"}
