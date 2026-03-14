from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from backend.api.utils import normalize_search_query, paginate_query
from backend.core.deps import PERMISSION_MANAGE_SUBCATEGORIES, require_permission
from backend.database import get_db
from backend.models.subcategory import SubCategory
from backend.schemas.common import StatusOut
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
    response: Response,
    q: str | None = Query(default=None, max_length=200),
    category_id: int | None = Query(default=None, ge=1),
    limit: int | None = Query(default=None, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_SUBCATEGORIES)),
):
    query = db.query(SubCategory)
    term = normalize_search_query(q)
    if term:
        query = query.filter(SubCategory.name.ilike(f"%{term}%"))
    if category_id is not None:
        query = query.filter(SubCategory.category_id == category_id)

    return paginate_query(
        query.order_by(SubCategory.id.asc()),
        response,
        limit=limit,
        offset=offset,
    )


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


@router.delete("/{subcategory_id}", response_model=StatusOut)
def delete_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_SUBCATEGORIES)),
):
    ok = SubCategoryService.delete(db, subcategory_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return {"status": "deleted"}
