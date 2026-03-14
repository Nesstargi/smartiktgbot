from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.api.utils import normalize_search_query, paginate_query
from backend.core.deps import PERMISSION_MANAGE_PRODUCTS, require_permission
from backend.database import get_db
from backend.models.product import Product
from backend.models.subcategory import SubCategory
from backend.schemas.common import StatusOut
from backend.schemas.product import ProductCreate, ProductOut, ProductUpdate
from backend.services.product_service import ProductService

router = APIRouter()


@router.post("/", response_model=ProductOut)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PRODUCTS)),
):
    return ProductService.create_product(db, data)


@router.get("/", response_model=list[ProductOut])
def get_all_products(
    response: Response,
    q: str | None = Query(default=None, max_length=200),
    category_id: int | None = Query(default=None, ge=1),
    subcategory_id: int | None = Query(default=None, ge=1),
    limit: int | None = Query(default=None, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PRODUCTS)),
):
    query = db.query(Product)
    term = normalize_search_query(q)
    if term:
        pattern = f"%{term}%"
        query = query.filter(
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
            )
        )
    if category_id is not None:
        query = query.join(SubCategory).filter(SubCategory.category_id == category_id)
    if subcategory_id is not None:
        query = query.filter(Product.subcategory_id == subcategory_id)

    return paginate_query(
        query.order_by(Product.id.asc()),
        response,
        limit=limit,
        offset=offset,
    )


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PRODUCTS)),
):
    product = ProductService.update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", response_model=StatusOut)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PRODUCTS)),
):
    ok = ProductService.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "deleted"}
