from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from bot.api_client import get_bot_admin_overview, get_bot_settings
from bot.handlers.catalog_common import schedule_bot_subscriber_sync

router = Router()

GROUP_CHAT_TYPES = {"group", "supergroup"}
GROUP_ADMIN_STATUSES = {"administrator", "creator"}

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Каталог")],
        [
            KeyboardButton(text="🔥 Акции"),
            KeyboardButton(text="❓ Консультация"),
        ],
        [KeyboardButton(text="ℹ️ О компании")],
    ],
    resize_keyboard=True,
)


def is_group_chat(message: Message) -> bool:
    return str(getattr(message.chat, "type", "")) in GROUP_CHAT_TYPES


def group_help_text() -> str:
    return (
        "Бот подключен к группе.\n\n"
        "Доступные команды:\n"
        "/stats - сводка по заявкам и аудитории\n"
        "/users - количество пользователей бота\n"
        "/orders - последние 10 заявок\n"
        "/orders 5 - последние 5 заявок (до 20)\n\n"
        "Команды с данными доступны только администраторам группы."
    )


def group_menu_remove() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def main_menu_reply_markup(message: Message):
    return group_menu_remove() if is_group_chat(message) else menu


async def _is_group_admin(message: Message) -> bool:
    if not message.from_user:
        return False

    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    return str(getattr(member, "status", "")) in GROUP_ADMIN_STATUSES


async def _ensure_group_admin(message: Message) -> bool:
    if not is_group_chat(message):
        await message.answer("Эта команда доступна только в группе с ботом.")
        return False

    if not await _is_group_admin(message):
        await message.answer("Эта команда доступна только администраторам группы.")
        return False

    return True


def _parse_orders_limit(text: str | None) -> int | None:
    raw = (text or "").strip()
    if not raw:
        return 10

    parts = raw.split(maxsplit=1)
    if len(parts) == 1:
        return 10

    try:
        limit = int(parts[1].strip())
    except ValueError:
        return None

    if limit < 1 or limit > 20:
        return None
    return limit


def _format_created_at(raw: str | None) -> str:
    if not raw:
        return "-"

    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return raw

    return value.strftime("%d.%m.%Y %H:%M")


def _compact_text(value: str | None, limit: int = 80) -> str:
    clean = (value or "-").strip() or "-"
    if len(clean) <= limit:
        return clean
    return f"{clean[: limit - 3].rstrip()}..."


def _format_recent_leads(overview: dict) -> str:
    recent_leads = overview.get("recent_leads") or []
    if not recent_leads:
        return "Заявок пока нет."

    lines = [f"Последние заявки: {len(recent_leads)} из {overview.get('leads_total', 0)}", ""]
    for index, item in enumerate(recent_leads, start=1):
        created_at = _format_created_at(item.get("created_at"))
        name = _compact_text(item.get("name"), limit=32)
        phone = _compact_text(item.get("phone"), limit=24)
        product = _compact_text(item.get("product"), limit=72)
        lines.append(f"{index}. {created_at} | {name} | {phone}")
        lines.append(f"   {product}")

    return "\n".join(lines)


@router.message(CommandStart())
async def start(msg: Message):
    if msg.from_user:
        schedule_bot_subscriber_sync(chat=msg.chat, user=msg.from_user)

    if is_group_chat(msg):
        await msg.answer(group_help_text(), reply_markup=group_menu_remove())
        return

    text = "Добро пожаловать! Выберите пункт меню 👇"
    try:
        settings = await get_bot_settings(force_refresh=True)
        if isinstance(settings, dict) and settings.get("start_message"):
            text = settings["start_message"]
    except Exception:
        pass

    await msg.answer(text, reply_markup=main_menu_reply_markup(msg))


@router.message(Command("help"))
async def help_command(message: Message):
    if is_group_chat(message):
        await message.answer(group_help_text(), reply_markup=group_menu_remove())
        return

    await message.answer("Используйте меню ниже для работы с ботом.", reply_markup=main_menu_reply_markup(message))


@router.message(Command("stats"))
async def group_stats(message: Message):
    if not await _ensure_group_admin(message):
        return

    overview = await get_bot_admin_overview(limit=1)
    await message.answer(
        "Сводка по боту\n\n"
        f"Пользователей бота: {overview.get('bot_users', 0)}\n"
        f"Всего заявок: {overview.get('leads_total', 0)}",
        reply_markup=group_menu_remove(),
    )


@router.message(Command("users"))
async def group_users(message: Message):
    if not await _ensure_group_admin(message):
        return

    overview = await get_bot_admin_overview(limit=1)
    await message.answer(
        f"Пользователей бота: {overview.get('bot_users', 0)}",
        reply_markup=group_menu_remove(),
    )


@router.message(Command("orders"))
async def group_orders(message: Message):
    if not await _ensure_group_admin(message):
        return

    limit = _parse_orders_limit(message.text)
    if limit is None:
        await message.answer(
            "Использование: /orders или /orders 5\nМожно запрашивать от 1 до 20 заявок.",
            reply_markup=group_menu_remove(),
        )
        return

    overview = await get_bot_admin_overview(limit=limit)
    await message.answer(_format_recent_leads(overview), reply_markup=group_menu_remove())
