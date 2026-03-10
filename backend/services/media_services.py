import os
import shutil
from fastapi import UploadFile
from uuid import uuid4

MEDIA_DIR = "backend/media"

os.makedirs(MEDIA_DIR, exist_ok=True)


class MediaService:
    @staticmethod
    async def save_file(file: UploadFile) -> str:

        # Сохраняем файл на диск с уникальным именем.
        # Возвращаем путь или file_id (для Telegram / CDN)

        ext = file.filename.split(".")[-1]
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
