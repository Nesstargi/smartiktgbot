import os
import shutil
from fastapi import UploadFile
from PIL import Image
from uuid import uuid4

MEDIA_DIR = "backend/media"

os.makedirs(MEDIA_DIR, exist_ok=True)


class MediaService:
    @staticmethod
    async def save_file(file: UploadFile) -> str:

        # Сохраняем файл на диск с уникальным именем.
        # Возвращаем путь или file_id (для Telegram / CDN)

        filename = (file.filename or "").lower()
        ext = filename.split(".")[-1] if "." in filename else ""

        # Конвертируем PNG -> JPG, чтобы Telegram стабильно принимал фото.
        if ext == "png":
            unique_name = f"{uuid4()}.jpg"
            path = os.path.join(MEDIA_DIR, unique_name)
            file.file.seek(0)
            image = Image.open(file.file)

            if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                image = image.convert("RGBA")
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            else:
                image = image.convert("RGB")

            image.save(path, format="JPEG", quality=90, optimize=True)
            return unique_name

        unique_name = f"{uuid4()}.{ext}"
        path = os.path.join(MEDIA_DIR, unique_name)

        # Сохраняем файл
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return unique_name

    @staticmethod
    def remove_file(file_path: str):
        # Удаляем файл, если нужен функционал удаления
        if os.path.exists(file_path):
            os.remove(file_path)
