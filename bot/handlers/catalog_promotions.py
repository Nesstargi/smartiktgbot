import asyncio

from aiogram import F
from aiogram.types import Message

from bot.api_client import get_promotions

from .catalog_common import (
    consultation_waiting_question,
    photo_payload,
    remember_sent_photo,
    router,
    send_photo_with_fallback,
)


@router.message(F.text == "🔥 Акции")
async def show_promotions(message: Message):
    consultation_waiting_question.pop(message.from_user.id if message.from_user else 0, None)
    promotions = await get_promotions()
    if not promotions:
        await message.answer("Сейчас активных акций нет.")
        return

    await message.answer("🔥 *Акции*", parse_mode="Markdown")

    photo_tasks: list[asyncio.Task | None] = []
    for item in promotions:
        image_url = item.get("image_url")
        photo_tasks.append(asyncio.create_task(photo_payload(image_url)) if image_url else None)

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
                        remember_sent_photo(item.get("image_url"), sent)
                        continue

                sent = await send_photo_with_fallback(
                    message,
                    photo,
                    caption=None,
                    image_url=item.get("image_url"),
                    parse_mode="Markdown",
                )
                if sent:
                    remember_sent_photo(item.get("image_url"), sent)
                    await message.answer(text, parse_mode="Markdown")
                    continue
            except Exception:
                pass
        await message.answer(text, parse_mode="Markdown")
