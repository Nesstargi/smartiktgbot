import asyncio
import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from bot.api_client import close_http_session
from bot.handlers.catalog import router as catalog_router
from bot.handlers.menu import router as menu_router

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(menu_router)
    dp.include_router(catalog_router)

    try:
        await dp.start_polling(bot)
    finally:
        await close_http_session()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
