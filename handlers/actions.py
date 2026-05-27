from aiogram import F, Router
from aiogram.types import CallbackQuery

from constants import ACTIVE_STATUSES
from keyboards.board import render_game_message
from services.game_runtime import locked_game
from services.game_state import color_for_user, finish_game, load_game, other_color, player_for_color, result_button_text
from services.telegram_safe import answer_callback

router = Router()


@router.callback_query(F.data == "bg:noop")
async def noop(callback: CallbackQuery):
    await answer_callback(callback)


@router.callback_query(F.data.regexp(r"^bg:resign:(chess|checkers):\d+$"))
async def resign_offer(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    async with locked_game(game_type, int(game_id_text)):
        await resign_offer_locked(callback, game_type, int(game_id_text))


async def resign_offer_locked(callback: CallbackQuery, game_type: str, game_id: int):
    game = await load_game(game_type, game_id)
    if game.status not in ACTIVE_STATUSES:
        await answer_callback(callback, "O'yin tugagan.", show_alert=True)
        return
    if not color_for_user(game, callback.from_user.id):
        await answer_callback(callback, "Bu sizning o'yiningiz emas.", show_alert=True)
        return
    user_color = color_for_user(game, callback.from_user.id)
    await finish_game(game_type, game, other_color(user_color), "resign")
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game, result_button_text(game))
    await answer_callback(callback, "Taslim bo'ldingiz.")


@router.callback_query(F.data.regexp(r"^bg:draw:(chess|checkers):\d+$"))
async def draw_offer(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    async with locked_game(game_type, int(game_id_text)):
        await draw_offer_locked(callback, game_type, int(game_id_text))


async def draw_offer_locked(callback: CallbackQuery, game_type: str, game_id: int):
    game = await load_game(game_type, game_id)
    user_color = color_for_user(game, callback.from_user.id)
    if not user_color:
        await answer_callback(callback, "Bu sizning o'yiningiz emas.", show_alert=True)
        return
    if game.status not in ACTIVE_STATUSES:
        await answer_callback(callback, "O'yin tugagan.", show_alert=True)
        return

    game.draw_offered_by = player_for_color(game, user_color)
    await game.save()
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game)
    await answer_callback(callback, "Durang taklif qilindi.")


@router.callback_query(F.data.regexp(r"^bg:draw_no:(chess|checkers):\d+$"))
async def draw_reject(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    async with locked_game(game_type, int(game_id_text)):
        await draw_reject_locked(callback, game_type, int(game_id_text))


async def draw_reject_locked(callback: CallbackQuery, game_type: str, game_id: int):
    game = await load_game(game_type, game_id)
    user_color = color_for_user(game, callback.from_user.id)
    if not user_color or not game.draw_offered_by_id:
        await answer_callback(callback, "Durang taklifi yo'q.", show_alert=True)
        return
    if game.draw_offered_by.user_id == callback.from_user.id:
        await answer_callback(callback, "Taklifga faqat raqib javob beradi.", show_alert=True)
        return
    game.draw_offered_by = None
    await game.save()
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game)
    await answer_callback(callback, "Durang rad etildi.")


@router.callback_query(F.data.regexp(r"^bg:draw_yes:(chess|checkers):\d+$"))
async def draw_accept(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    async with locked_game(game_type, int(game_id_text)):
        await draw_accept_locked(callback, game_type, int(game_id_text))


async def draw_accept_locked(callback: CallbackQuery, game_type: str, game_id: int):
    game = await load_game(game_type, game_id)
    if not game.draw_offered_by_id:
        await answer_callback(callback, "Durang taklifi yo'q.", show_alert=True)
        return
    if game.draw_offered_by.user_id == callback.from_user.id:
        await answer_callback(callback, "Taklifga faqat raqib javob beradi.", show_alert=True)
        return
    if not color_for_user(game, callback.from_user.id):
        await answer_callback(callback, "Bu sizning o'yiningiz emas.", show_alert=True)
        return

    await finish_game(game_type, game, None, "draw")
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game, result_button_text(game))
    await answer_callback(callback, "Durang qabul qilindi.")
