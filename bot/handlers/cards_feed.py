from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.api_client import get_products

router = Router()


@router.callback_query(F.data.startswith("sub_"))
async def show_products(callback: CallbackQuery):
    sub_id = int(callback.data.split("_")[1])
    products = await get_products(sub_id)

    if not products:
        await callback.message.answer("❌ В этой подкатегории пока нет товаров")
        return

    await callback.message.delete()

    for p in products:
        text = (
            f" *{p['name']}*\n"
            f"━━━━━━━━━━━━━━\n"
            f"🧾 {p.get('description') or '—'}\n"
            f"━━━━━━━━━━━━━━"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📝 Оставить заявку", callback_data=f"lead_{p['id']}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Назад", callback_data="back_to_subcategories"
                    )
                ],
            ]
        )

        await callback.message.answer_photo(
            photo=p["image_file_id"],
            caption=text,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
