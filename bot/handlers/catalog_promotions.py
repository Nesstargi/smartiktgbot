import asyncio

from aiogram import F
from aiogram.types import Message

from bot.api_client import get_promotions, update_promotion_file_id

from .catalog_common import (
    clear_consultation_waiting,
    photo_payload,
    remember_sent_photo,
    router,
    send_photo_with_fallback,
)


@router.message(F.text == "🔥 Акции")
async def show_promotions(message: Message):
    if message.from_user:
        await clear_consultation_waiting(message.from_user.id)
    promotions = await get_promotions()
    if not promotions:
        await message.answer("Сейчас активных акций нет.")
        return

    await message.answer("🔥 *Акции*", parse_mode="Markdown")

    photo_tasks: list[asyncio.Task | None] = []
    for item in promotions:
        image_url = item.get("image_url")
        image_file_id = item.get("image_file_id")
        image_ref = image_file_id or image_url
        photo_tasks.append(asyncio.create_task(photo_payload(image_ref)) if image_ref else None)

    for item, task in zip(promotions, photo_tasks):
        title = item.get("title", "Без названия")
        desc = item.get("description") or ""
        text = f"*{title}*\n{desc}".strip()

        try:
            photo = await task if task else None
        except Exception:
            photo = None
        if photo:
            try:
                if len(text) <= 1024:
                    sent = await send_photo_with_fallback(
                        message,
                        photo,
                        caption=text,
                        image_url=item.get("image_url"),
                        parse_mode="Markdown",
                    )
                    if sent:
                        image_url = item.get("image_url")
                        if image_url:
                            await remember_sent_photo(image_url, sent)
                        if not item.get("image_file_id"):
                            photo_sizes = getattr(sent, "photo", None)
                            if photo_sizes:
                                file_id = photo_sizes[-1].file_id
                                await update_promotion_file_id(item.get("id"), file_id)
                                item["image_file_id"] = file_id
                        continue

                sent = await send_photo_with_fallback(
                    message,
                    photo,
                    caption=None,
                    image_url=item.get("image_url"),
                    parse_mode="Markdown",
                )
                if sent:
                    image_url = item.get("image_url")
                    if image_url:
                        await remember_sent_photo(image_url, sent)
                    if not item.get("image_file_id"):
                        photo_sizes = getattr(sent, "photo", None)
                        if photo_sizes:
                            file_id = photo_sizes[-1].file_id
                            await update_promotion_file_id(item.get("id"), file_id)
                            item["image_file_id"] = file_id
                    await message.answer(text, parse_mode="Markdown")
                    continue
            except Exception:
                pass
        await message.answer(text, parse_mode="Markdown")
