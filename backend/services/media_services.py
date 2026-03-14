import asyncio
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError


MEDIA_DIR = Path(__file__).resolve().parents[1] / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

MAX_IMAGE_DIMENSION = 1600
JPEG_QUALITY = 85


def _media_dir() -> Path:
    return Path(MEDIA_DIR)


def _image_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image = image.convert("RGBA")
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.getchannel("A"))
        return background

    if image.mode != "RGB":
        return image.convert("RGB")

    return image


def _normalize_image(upload_bytes: bytes) -> tuple[str, bytes]:
    try:
        with Image.open(BytesIO(upload_bytes)) as image:
            image = ImageOps.exif_transpose(image)
            image.load()
            image = _image_to_rgb(image)
            image.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)

            buffer = BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=JPEG_QUALITY,
                optimize=True,
                progressive=True,
            )
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Invalid image file") from exc

    return f"{uuid4()}.jpg", buffer.getvalue()


class MediaService:
    @staticmethod
    async def save_file(file: UploadFile) -> str:
        upload_bytes = await file.read()
        if not upload_bytes:
            raise ValueError("Empty image file")

        filename, processed_bytes = await asyncio.to_thread(_normalize_image, upload_bytes)
        media_dir = _media_dir()
        await asyncio.to_thread(media_dir.mkdir, parents=True, exist_ok=True)
        path = media_dir / filename
        await asyncio.to_thread(path.write_bytes, processed_bytes)
        return filename

    @staticmethod
    def remove_file(file_path: str):
        path = Path(file_path)
        if path.exists():
            path.unlink()
