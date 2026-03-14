from fastapi import APIRouter, Depends, HTTPException, UploadFile

from backend.core.deps import (
    PERMISSION_MANAGE_CATEGORIES,
    PERMISSION_MANAGE_PRODUCTS,
    PERMISSION_MANAGE_PROMOTIONS,
    PERMISSION_MANAGE_SUBCATEGORIES,
    require_any_permission,
)
from backend.services.media_services import MediaService

router = APIRouter()

ALLOWED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".jfif")


@router.post("/file")
async def upload_file(
    file: UploadFile,
    admin=Depends(
        require_any_permission(
            [
                PERMISSION_MANAGE_CATEGORIES,
                PERMISSION_MANAGE_SUBCATEGORIES,
                PERMISSION_MANAGE_PRODUCTS,
                PERMISSION_MANAGE_PROMOTIONS,
            ]
        )
    ),
):
    filename = (file.filename or "").lower()
    if not filename.endswith(ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Allowed image formats: png, jpg, jpeg, webp, jfif",
        )

    try:
        saved_filename = await MediaService.save_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "filename": saved_filename,
        "url": f"/media/{saved_filename}",
    }
