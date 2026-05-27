from asyncio import run
from logging import INFO, basicConfig

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import Config
from handlers.board_games import router as board_games_router
from models import init_db

basicConfig(level=INFO)


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="profile", description="Profil va shaxmat statistikasi"),
            BotCommand(command="top", description="Reyting bo'yicha TOP"),
            BotCommand(command="chesswhite", description="Oq rangda o'yin yaratish"),
            BotCommand(command="chessblack", description="Qora rangda o'yin yaratish"),
        ]
    )


async def main():
    if not Config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN .env ichida berilmagan.")

    await init_db()

    bot = Bot(token=Config.BOT_TOKEN)
    await set_bot_commands(bot)

    dp = Dispatcher()
    dp.include_router(board_games_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
