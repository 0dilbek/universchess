from asyncio import CancelledError, create_task, run
from contextlib import suppress
from logging import INFO, basicConfig

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import Config
from handlers.board_games import router as board_games_router
from models import init_db
from services.game_watchdog import run_time_watchdog

basicConfig(level=INFO)


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="profile", description="Profil va shaxmat statistikasi"),
            BotCommand(command="top", description="Reyting bo'yicha TOP"),
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
    watchdog_task = create_task(run_time_watchdog(bot))
    try:
        await dp.start_polling(bot)
    finally:
        watchdog_task.cancel()
        with suppress(CancelledError):
            await watchdog_task


if __name__ == "__main__":
    run(main())
