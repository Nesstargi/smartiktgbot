import asyncio
from aiogram import Bot, Dispatcher

from bot.handlers.menu import router as menu_router
from bot.handlers.catalog import router as catalog_router

TOKEN = "8089665241:AAGC9YQJN4-pmkOrLhSDhKYnBMFqe5fnlrY"


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Роутеры
    dp.include_router(menu_router)
    dp.include_router(catalog_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
