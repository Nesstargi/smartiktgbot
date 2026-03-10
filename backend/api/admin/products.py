from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.deps import PERMISSION_MANAGE_PRODUCTS, require_permission
from backend.database import get_db
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
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PRODUCTS)),
):
    return ProductService.list_products(db)


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


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PRODUCTS)),
):
    ok = ProductService.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "deleted"}
