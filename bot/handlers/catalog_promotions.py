from aiogram import F
from aiogram.types import Message

from bot.api_client import get_promotions

from .catalog_common import (
    consultation_waiting_question,
    photo_payload,
    remember_sent_photo,
    router,
)


@router.message(F.text == "🔥 Акции")
async def show_promotions(message: Message):
    consultation_waiting_question.pop(message.from_user.id if message.from_user else 0, None)
    promotions = await get_promotions()
    if not promotions:
        await message.answer("Сейчас активных акций нет.")
        return

    await message.answer("🔥 *Акции*", parse_mode="Markdown")
    for item in promotions:
        title = item.get("title", "Без названия")
        desc = item.get("description") or ""
        text = f"*{title}*\n{desc}".strip()

        photo = await photo_payload(item.get("image_url"))
        if photo:
            try:
                sent = await message.answer_photo(photo=photo, caption=text, parse_mode="Markdown")
                remember_sent_photo(item.get("image_url"), sent)
                continue
            except Exception:
                pass
        await message.answer(text, parse_mode="Markdown")
