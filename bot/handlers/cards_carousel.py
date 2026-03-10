from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.api_client import get_products

router = Router()

memory = {}  # sub_id -> index


@router.callback_query(F.data.startswith("sub_"))
async def show_carousel(callback: CallbackQuery):
    sub_id = int(callback.data.split("_")[1])
    products = await get_products(sub_id)

    if not products:
        return

    memory[sub_id] = 0
    p = products[0]

    await send_card(callback, sub_id, products, 0)


@router.callback_query(F.data.startswith("next_"))
async def next_card(callback: CallbackQuery):
    _, sub_id, idx = callback.data.split("_")
    sub_id, idx = int(sub_id), int(idx)

    products = await get_products(sub_id)
    idx = (idx + 1) % len(products)
    memory[sub_id] = idx

    await send_card(callback, sub_id, products, idx)


@router.callback_query(F.data.startswith("prev_"))
async def prev_card(callback: CallbackQuery):
    _, sub_id, idx = callback.data.split("_")
    sub_id, idx = int(sub_id), int(idx)

    products = await get_products(sub_id)
    idx = (idx - 1) % len(products)
    memory[sub_id] = idx

    await send_card(callback, sub_id, products, idx)


async def send_card(callback, sub_id, products, idx):
    p = products[idx]

    text = f"📦 *{p['name']}*\n\n📝 {p.get('description') or '—'}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"prev_{sub_id}_{idx}"),
                InlineKeyboardButton(text="📝 Заявка", callback_data=f"lead_{p['id']}"),
                InlineKeyboardButton(text="➡️", callback_data=f"next_{sub_id}_{idx}"),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад", callback_data="back_to_subcategories"
                )
            ],
        ]
    )

    await callback.message.edit_media(
        media={
            "type": "photo",
            "media": p["image_file_id"],
            "caption": text,
            "parse_mode": "Markdown",
        },
        reply_markup=keyboard,
    )
