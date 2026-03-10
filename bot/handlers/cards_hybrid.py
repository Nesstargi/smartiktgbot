from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.callback_query(F.data.startswith("sub_"))
async def hybrid_menu(callback: CallbackQuery):
    sub_id = int(callback.data.split("_")[1])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎠 Смотреть каруселью", callback_data=f"carousel_{sub_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Смотреть списком", callback_data=f"feed_{sub_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад", callback_data="back_to_subcategories"
                )
            ],
        ]
    )

    await callback.message.edit_text("🧭 Как показать товары?", reply_markup=keyboard)
