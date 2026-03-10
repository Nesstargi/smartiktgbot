import aiohttp
from pathlib import Path
from urllib.parse import urlparse

from backend.config import TELEGRAM_BOT_TOKEN


class NotificationService:
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
            if host in {"localhost", "127.0.0.1"} and parsed.path.startswith("/media/"):
                candidate = Path("backend/media") / parsed.path.removeprefix("/media/")
                if candidate.exists() and candidate.is_file():
                    return candidate
            # Public remote URL can be sent to Telegram directly.
            return None

        if value.startswith("/media/"):
            candidate = Path("backend/media") / value.removeprefix("/media/")
        elif value.startswith("media/"):
            candidate = Path("backend/media") / value.removeprefix("media/")
        else:
            candidate = Path(value)

        if candidate.exists() and candidate.is_file():
            return candidate

        return None

    @staticmethod
    async def send_broadcast(
        chat_ids: list[str],
        title: str,
        message: str,
        image_url: str | None = None,
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

        success = 0
        failed = 0

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for chat_id in unique_chat_ids:
                try:
                    if image_url:
                        if local_image_path:
                            data = aiohttp.FormData()
                            data.add_field("chat_id", chat_id)
                            data.add_field("caption", text)
                            data.add_field("parse_mode", "Markdown")
                            with local_image_path.open("rb") as photo_file:
                                data.add_field(
                                    "photo",
                                    photo_file,
                                    filename=local_image_path.name,
                                    content_type="application/octet-stream",
                                )
                                async with session.post(f"{base_url}/sendPhoto", data=data) as resp:
                                    if resp.status == 200:
                                        success += 1
                                    else:
                                        failed += 1
                        else:
                            payload = {
                                "chat_id": chat_id,
                                "photo": image_url,
                                "caption": text,
                                "parse_mode": "Markdown",
                            }
                            async with session.post(f"{base_url}/sendPhoto", json=payload) as resp:
                                if resp.status == 200:
                                    success += 1
                                else:
                                    failed += 1
                    else:
                        payload = {
                            "chat_id": chat_id,
                            "text": text,
                            "parse_mode": "Markdown",
                        }
                        async with session.post(f"{base_url}/sendMessage", json=payload) as resp:
                            if resp.status == 200:
                                success += 1
                            else:
                                failed += 1
                except Exception:
                    failed += 1

        return {
            "total": len(unique_chat_ids),
            "success": success,
            "failed": failed,
        }
