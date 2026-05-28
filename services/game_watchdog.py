from asyncio import CancelledError, sleep

from aiogram import Bot

from keyboards.board import game_markup, game_text
from models.board_game import CheckersGame, ChessGame
from services.game_runtime import locked_game
from services.game_state import finish_game, load_game, other_color, result_button_text
from services.telegram_safe import edit_bot_message_text
from services.time_control import current_time_left, timed_out_color, utc_now

WATCHDOG_INTERVAL = 30


async def run_time_watchdog(bot: Bot) -> None:
    while True:
        try:
            await check_active_games(bot)
            await sleep(WATCHDOG_INTERVAL)
        except CancelledError:
            raise
        except Exception:
            await sleep(WATCHDOG_INTERVAL)


async def check_active_games(bot: Bot) -> None:
    chess_games = await ChessGame.filter(status="active").values_list("id", flat=True)
    checkers_games = await CheckersGame.filter(status="active").values_list("id", flat=True)

    for game_id in chess_games:
        await safe_check_game(bot, "chess", game_id)
    for game_id in checkers_games:
        await safe_check_game(bot, "checkers", game_id)


async def safe_check_game(bot: Bot, game_type: str, game_id: int) -> None:
    try:
        await check_game(bot, game_type, game_id)
    except Exception:
        return


async def check_game(bot: Bot, game_type: str, game_id: int) -> None:
    async with locked_game(game_type, int(game_id)):
        game = await load_game(game_type, int(game_id))
        if game.status != "active" or (not game.message_id and not game.inline_message_id):
            return

        now = utc_now()
        timeout_color = timed_out_color(game, now)
        result_text = None

        if timeout_color:
            if timeout_color == "white":
                game.white_time_left = 0
            else:
                game.black_time_left = 0
            await finish_game(game_type, game, other_color(timeout_color), "timeout")
            game = await load_game(game_type, game.id)
            result_text = result_button_text(game)
        else:
            if game.turn == "white":
                game.white_time_left = current_time_left(game, "white", now)
            else:
                game.black_time_left = current_time_left(game, "black", now)
            game.last_move_at = now
            await game.save(update_fields=["white_time_left", "black_time_left", "last_move_at", "updated_at"])

        text = game_text(game_type, game)
        if result_text:
            text = f"{text}\n\n{result_text}"
        edit_kwargs = {"text": text, "reply_markup": game_markup(game_type, game, result_text)}
        if game.inline_message_id:
            edit_kwargs["inline_message_id"] = game.inline_message_id
        else:
            edit_kwargs["chat_id"] = game.chat_id
            edit_kwargs["message_id"] = game.message_id
        await edit_bot_message_text(bot, **edit_kwargs)
