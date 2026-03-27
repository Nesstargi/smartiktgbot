import asyncio
import logging
from html import escape

from aiogram import F
from aiogram.types import Message

from bot.api_client import get_promotions, update_promotion_file_id

from .catalog_common import (
    clear_consultation_waiting,
    photo_payload,
    remember_sent_photo,
    router,
    schedule_bot_subscriber_sync,
    send_photo_with_fallback,
)

logger = logging.getLogger(__name__)


def _promotion_texts(item: dict) -> tuple[str, str]:
    title = str(item.get("title") or "Без названия")
    desc = str(item.get("description") or "")

    plain_text = "\n".join(part for part in (title, desc) if part).strip()
    html_title = escape(title)
    html_desc = escape(desc)
    html_text = "\n".join(
        part
        for part in (f"<b>{html_title}</b>", html_desc)
        if part
    ).strip()
    return html_text, plain_text or title


async def _send_promotion_text(message: Message, html_text: str, plain_text: str) -> bool:
    try:
        await message.answer(html_text, parse_mode="HTML")
        return True
    except Exception:
        logger.debug("Failed to send promotion text with HTML formatting", exc_info=True)

    try:
        await message.answer(plain_text)
        return True
    except Exception:
        logger.debug("Failed to send promotion text without formatting", exc_info=True)
        return False


async def _send_promotion_photo(
    message: Message,
    photo,
    html_text: str,
    plain_text: str,
    image_url: str | None,
):
    if len(html_text) <= 1024:
        sent = await send_photo_with_fallback(
            message,
            photo,
            caption=html_text,
            image_url=image_url,
            parse_mode="HTML",
        )
        if sent:
            return sent

    sent = await send_photo_with_fallback(
        message,
        photo,
        caption=None,
        image_url=image_url,
        parse_mode="HTML",
    )
    if sent:
        await _send_promotion_text(message, html_text, plain_text)
    return sent


@router.message(F.text == "🔥 Акции")
async def show_promotions(message: Message):
    if message.from_user:
        schedule_bot_subscriber_sync(chat=message.chat, user=message.from_user)
        await clear_consultation_waiting(message.from_user.id)
    promotions = await get_promotions(force_refresh=True)
    if not promotions:
        await message.answer("Сейчас активных акций нет.")
        return

    await message.answer("🔥 Акции")

    photo_tasks: list[asyncio.Task | None] = []
    image_url_fallback_tasks: list[asyncio.Task | None] = []
    for item in promotions:
        image_url = item.get("image_url")
        image_file_id = item.get("image_file_id")
        image_ref = image_file_id or image_url
        photo_tasks.append(asyncio.create_task(photo_payload(image_ref)) if image_ref else None)
        image_url_fallback_tasks.append(
            asyncio.create_task(photo_payload(image_url))
            if image_file_id and image_url
            else None
        )

    for item, task, fallback_task in zip(promotions, photo_tasks, image_url_fallback_tasks):
        html_text, plain_text = _promotion_texts(item)
        image_url = item.get("image_url")
        image_file_id = item.get("image_file_id")
        sent = None
        used_image_url_fallback = False

        try:
            photo = await task if task else None
        except Exception:
            logger.debug(
                "Failed to resolve promotion photo for promotion_id=%s",
                item.get("id"),
                exc_info=True,
            )
            photo = None

        if photo:
            try:
                sent = await _send_promotion_photo(
                    message,
                    photo,
                    html_text,
                    plain_text,
                    image_url,
                )
            except Exception:
                logger.debug(
                    "Failed to send promotion photo via primary ref for promotion_id=%s",
                    item.get("id"),
                    exc_info=True,
                )

        if not sent and fallback_task:
            try:
                fallback_photo = await fallback_task
            except Exception:
                logger.debug(
                    "Failed to resolve promotion image_url fallback for promotion_id=%s",
                    item.get("id"),
                    exc_info=True,
                )
                fallback_photo = None

            if fallback_photo:
                try:
                    sent = await _send_promotion_photo(
                        message,
                        fallback_photo,
                        html_text,
                        plain_text,
                        image_url,
                    )
                    used_image_url_fallback = bool(sent)
                except Exception:
                    logger.debug(
                        "Failed to send promotion photo via image_url fallback for promotion_id=%s",
                        item.get("id"),
                        exc_info=True,
                    )

        if sent:
            if image_url:
                await remember_sent_photo(image_url, sent)

            photo_sizes = getattr(sent, "photo", None)
            should_refresh_file_id = bool(photo_sizes) and (
                used_image_url_fallback or not image_file_id
            )
            if should_refresh_file_id:
                file_id = photo_sizes[-1].file_id
                await update_promotion_file_id(item.get("id"), file_id)
                item["image_file_id"] = file_id
            continue

        await _send_promotion_text(message, html_text, plain_text)
