import asyncio
import logging
import os

from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.api_client import create_lead, get_bot_settings
from bot.handlers.menu import menu

from .catalog_common import (
    DEFAULT_ABOUT_MESSAGE,
    DEFAULT_CONSULTATION_CONTACT_PROMPT,
    DEFAULT_CONSULTATION_MESSAGE,
    DEFAULT_CONSULTATION_PHONE,
    cancel_reminder_task,
    clear_consultation_waiting,
    clear_reminder_reply_context,
    get_reminder_reply_context,
    is_consultation_waiting,
    lead_contact_keyboard,
    pop_lead_request,
    pop_reminder_reply_context,
    router,
    set_consultation_waiting,
    set_lead_request,
)

logger = logging.getLogger(__name__)
LEADS_GROUP_CHAT_ID = os.getenv("TELEGRAM_LEADS_CHAT_ID", "").strip()


def _parse_chat_id(raw: str):
    if not raw:
        return None
    value = raw.strip().strip('"').strip("'")
    try:
        return int(value)
    except ValueError:
        return value


def is_menu_text(text: str | None) -> bool:
    return text in {
        "❌ Отмена",
        "🏠 Главное меню",
        "🛒 Каталог",
        "🔥 Акции",
        "❓ Консультация",
        "ℹ️ О компании",
    }


async def accept_reminder_response(message: Message, context: dict):
    user = message.from_user
    if not user:
        return

    await set_lead_request(
        user.id,
        {
            **context,
            "user_message": message.text,
        },
    )
    await clear_reminder_reply_context(user.id)

    await message.answer(
        "Спасибо за ответ. Теперь нажмите кнопку и поделитесь номером телефона:",
        reply_markup=lead_contact_keyboard(),
    )


async def notify_lead_to_group(
    message: Message,
    *,
    name: str,
    phone: str,
    telegram_id: int,
    product: str,
):
    chat_id = _parse_chat_id(LEADS_GROUP_CHAT_ID)
    if not chat_id:
        logger.warning("Lead group notify skipped: TELEGRAM_LEADS_CHAT_ID is empty")
        return

    user = message.from_user
    username = f"@{user.username}" if user and user.username else "-"

    text = (
        "Новый лид из бота\n\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Telegram ID: {telegram_id}\n"
        f"Username: {username}\n"
        f"Заявка: {product or '-'}"
    )

    try:
        await message.bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        # Test-mode notification should not break user flow.
        logger.exception("Lead group notify failed for chat_id=%s: %s", chat_id, e)


@router.message(F.text == "❓ Консультация")
async def start_consultation(message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    await asyncio.gather(
        clear_reminder_reply_context(user_id),
        set_consultation_waiting(user_id),
    )

    try:
        settings = await get_bot_settings()
    except Exception:
        settings = {}

    phone = settings.get("consultation_phone") or DEFAULT_CONSULTATION_PHONE
    template = settings.get("consultation_message") or DEFAULT_CONSULTATION_MESSAGE

    try:
        text = template.format(phone=phone)
    except Exception:
        text = f"{template}\n\nТелефон: {phone}"

    await message.answer(text, reply_markup=menu)


@router.message(F.text == "ℹ️ О компании")
async def show_about(message: Message):
    if message.from_user:
        await clear_consultation_waiting(message.from_user.id)

    try:
        settings = await get_bot_settings()
    except Exception:
        settings = {}

    text = settings.get("about_message") or DEFAULT_ABOUT_MESSAGE
    await message.answer(text, reply_markup=menu)


@router.message(F.reply_to_message, F.text)
async def reminder_reply(message: Message):
    user = message.from_user
    if not user:
        return

    context = await get_reminder_reply_context(user.id)
    if not context:
        return

    prompt_id = context.get("prompt_message_id")
    if not prompt_id or message.reply_to_message.message_id != prompt_id:
        return

    await accept_reminder_response(message, context)


@router.message(F.text == "❌ Отмена")
async def cancel_lead(message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    context = await pop_lead_request(user_id)
    await asyncio.gather(
        pop_reminder_reply_context(user_id),
        clear_consultation_waiting(user_id),
        cancel_reminder_task(user_id),
    )

    inline = None
    if context:
        sub_id = context.get("sub_id")
        product_id = context.get("product_id")
        if sub_id and product_id:
            inline = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="↩ Вернуться к товару", callback_data=f"prod_{sub_id}_{product_id}")],
                    [InlineKeyboardButton(text="↩ К списку товаров", callback_data=f"sub_{sub_id}")],
                ]
            )

    await message.answer("Ок, отменили заявку.", reply_markup=inline)


@router.message(F.text == "🏠 Главное меню")
async def back_to_main_from_keyboard(message: Message):
    if message.from_user:
        await clear_consultation_waiting(message.from_user.id)
    await message.answer("🏠 Главное меню\n\nВыберите пункт меню 👇", reply_markup=menu)


@router.message(F.text)
async def reminder_reply_fallback(message: Message):
    user = message.from_user
    if not user:
        return

    if is_menu_text(message.text):
        return

    if await is_consultation_waiting(user.id):
        await asyncio.gather(
            clear_consultation_waiting(user.id),
            clear_reminder_reply_context(user.id),
        )

        await set_lead_request(
            user.id,
            {
                "chat_id": message.chat.id,
                "flow": "consultation",
                "user_message": message.text,
            },
        )

        try:
            settings = await get_bot_settings()
            contact_prompt = settings.get("consultation_contact_prompt") or DEFAULT_CONSULTATION_CONTACT_PROMPT
        except Exception:
            contact_prompt = DEFAULT_CONSULTATION_CONTACT_PROMPT

        await message.answer(contact_prompt, reply_markup=lead_contact_keyboard())
        return

    context = await get_reminder_reply_context(user.id)
    if not context:
        return

    await accept_reminder_response(message, context)


@router.message(F.contact)
async def handle_contact(message: Message):
    if not message.from_user:
        return

    phone = message.contact.phone_number
    user_id = message.from_user.id
    name = message.from_user.full_name
    context = await pop_lead_request(user_id) or {}
    await asyncio.gather(
        pop_reminder_reply_context(user_id),
        clear_consultation_waiting(user_id),
        cancel_reminder_task(user_id),
    )

    flow = context.get("flow")
    product_id = context.get("product_id")
    product_name = context.get("product_name")
    user_message = context.get("user_message")

    product_value = str(product_id) if product_id is not None else ""
    if product_name:
        product_value = f"{product_name} (id={product_id})"
    if flow == "consultation":
        product_value = "Консультация"
    if user_message:
        suffix = f"сообщение клиента: {user_message}"
        product_value = f"{product_value} | {suffix}" if product_value else suffix

    await create_lead(
        {
            "name": name,
            "phone": phone,
            "telegram_id": user_id,
            "product": product_value,
        }
    )

    await notify_lead_to_group(
        message,
        name=name,
        phone=phone,
        telegram_id=user_id,
        product=product_value,
    )

    await message.answer(
        "✅ Заявка отправлена!\n\nНаш менеджер скоро свяжется с вами 📞",
        reply_markup=menu,
    )
