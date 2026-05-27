from asyncio import run
from logging import INFO, basicConfig

from aiogram import Bot, Dispatcher

from config import Config
from handlers.board_games import router as board_games_router
from models import init_db

basicConfig(level=INFO)


async def main():
    if not Config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN .env ichida berilmagan.")

    await init_db()

    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(board_games_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
