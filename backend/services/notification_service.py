import asyncio
import mimetypes
from pathlib import Path
from urllib.parse import urlparse

import aiohttp

from backend.config import TELEGRAM_BOT_TOKEN

MEDIA_ROOT = Path(__file__).resolve().parents[1] / "media"
MEDIA_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "backend"}
BROADCAST_CONCURRENCY = 10


class NotificationService:
    @staticmethod
    def is_configured() -> bool:
        return bool(TELEGRAM_BOT_TOKEN)

    @staticmethod
    def _resolve_local_media_path(image_url: str | None) -> Path | None:
        if not image_url:
            return None

        value = str(image_url).strip()
        if not value:
            return None

        if value.startswith("http://") or value.startswith("https://"):
            parsed = urlparse(value)
            host = (parsed.hostname or "").lower()
            if host in MEDIA_HOSTS and parsed.path.startswith("/media/"):
                candidate = MEDIA_ROOT / parsed.path.removeprefix("/media/")
                if candidate.exists() and candidate.is_file():
                    return candidate
            # Public remote URL can be sent to Telegram directly.
            return None

        if value.startswith("/media/"):
            candidate = MEDIA_ROOT / value.removeprefix("/media/")
        elif value.startswith("media/"):
            candidate = MEDIA_ROOT / value.removeprefix("media/")
        else:
            candidate = Path(value)

        if candidate.exists() and candidate.is_file():
            return candidate

        return None

    @staticmethod
    def _content_type_for(path: Path) -> str:
        return mimetypes.guess_type(path.name)[0] or "application/octet-stream"

    @staticmethod
    async def send_broadcast(
        chat_ids: list[str],
        title: str,
        message: str,
        image_url: str | None = None,
        image_file_id: str | None = None,
    ):
        token = TELEGRAM_BOT_TOKEN
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not set for backend notifications")

        unique_chat_ids = []
        seen = set()
        for raw in chat_ids:
            if raw is None:
                continue
            value = str(raw).strip()
            if not value or value in seen:
                continue
            seen.add(value)
            unique_chat_ids.append(value)

        text = f"*{title}*\n\n{message}".strip()
        base_url = f"https://api.telegram.org/bot{token}"
        local_image_path = NotificationService._resolve_local_media_path(image_url)
        local_image_bytes = None
        local_image_name = None
        local_image_content_type = None
        if local_image_path:
            local_image_bytes = await asyncio.to_thread(local_image_path.read_bytes)
            local_image_name = local_image_path.name
            local_image_content_type = NotificationService._content_type_for(local_image_path)

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            semaphore = asyncio.Semaphore(BROADCAST_CONCURRENCY)

            async def send_to_chat(chat_id: str) -> bool:
                async with semaphore:
                    try:
                        if image_file_id:
                            payload = {
                                "chat_id": chat_id,
                                "photo": image_file_id,
                                "caption": text,
                                "parse_mode": "Markdown",
                            }
                            async with session.post(f"{base_url}/sendPhoto", json=payload) as resp:
                                return resp.status == 200

                        if image_url:
                            if local_image_bytes and local_image_name:
                                data = aiohttp.FormData()
                                data.add_field("chat_id", chat_id)
                                data.add_field("caption", text)
                                data.add_field("parse_mode", "Markdown")
                                data.add_field(
                                    "photo",
                                    local_image_bytes,
                                    filename=local_image_name,
                                    content_type=local_image_content_type,
                                )
                                async with session.post(f"{base_url}/sendPhoto", data=data) as resp:
                                    return resp.status == 200

                            payload = {
                                "chat_id": chat_id,
                                "photo": image_url,
                                "caption": text,
                                "parse_mode": "Markdown",
                            }
                            async with session.post(f"{base_url}/sendPhoto", json=payload) as resp:
                                return resp.status == 200

                        payload = {
                            "chat_id": chat_id,
                            "text": text,
                            "parse_mode": "Markdown",
                        }
                        async with session.post(f"{base_url}/sendMessage", json=payload) as resp:
                            return resp.status == 200
                    except Exception:
                        return False

            results = await asyncio.gather(
                *(send_to_chat(chat_id) for chat_id in unique_chat_ids),
                return_exceptions=False,
            )

        success = sum(1 for item in results if item)
        failed = len(results) - success

        return {
            "total": len(unique_chat_ids),
            "success": success,
            "failed": failed,
        }
