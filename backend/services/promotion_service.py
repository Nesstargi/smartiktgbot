from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.promotion import Promotion
from backend.schemas.promotion import PromotionCreate, PromotionUpdate


class PromotionService:
    @staticmethod
    def _find_by_normalized_title(db: Session, title: str):
        return (
            db.query(Promotion)
            .filter(func.lower(Promotion.title) == title.lower())
            .first()
        )

    @staticmethod
    def list_all(db: Session):
        return db.query(Promotion).order_by(Promotion.id.desc()).all()

    @staticmethod
    def list_active(db: Session):
        return (
            db.query(Promotion)
            .filter(Promotion.is_active.is_(True))
            .order_by(Promotion.id.desc())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, promotion_id: int):
        return db.query(Promotion).filter(Promotion.id == promotion_id).first()

    @staticmethod
    def create(db: Session, data: PromotionCreate):
        payload = data.model_dump(exclude={"send_to_all"})
        existing = PromotionService._find_by_normalized_title(db, payload["title"])
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Promotion with this title already exists",
            )

        item = Promotion(**payload)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update(db: Session, promotion_id: int, data: PromotionUpdate):
        item = PromotionService.get_by_id(db, promotion_id)
        if not item:
            return None

        payload = data.model_dump(exclude_unset=True)
        if "title" in payload:
            existing = PromotionService._find_by_normalized_title(db, payload["title"])
            if existing and existing.id != promotion_id:
                raise HTTPException(
                    status_code=409,
                    detail="Promotion with this title already exists",
                )

        for key, value in payload.items():
            setattr(item, key, value)

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, promotion_id: int):
        item = PromotionService.get_by_id(db, promotion_id)
        if not item:
            return False

        db.delete(item)
        db.commit()
        return True
