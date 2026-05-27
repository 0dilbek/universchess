from aiogram import F, Router
from aiogram.types import CallbackQuery

from constants import ACTIVE_STATUSES
from keyboards.board import render_game_message, resign_confirm_keyboard
from services.game_state import color_for_user, finish_game, load_game, other_color, player_for_color, result_button_text

router = Router()


@router.callback_query(F.data == "bg:noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("bg:resign:"))
async def resign_offer(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    game = await load_game(game_type, int(game_id_text))
    if game.status not in ACTIVE_STATUSES:
        await callback.answer("O'yin tugagan.", show_alert=True)
        return
    if not color_for_user(game, callback.from_user.id):
        await callback.answer("Bu sizning o'yiningiz emas.", show_alert=True)
        return
    await callback.message.edit_reply_markup(reply_markup=resign_confirm_keyboard(game_type, game.id))
    await callback.answer("Taslim bo'lishni tasdiqlang.")


@router.callback_query(F.data.startswith("bg:resign_no:"))
async def resign_cancel(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    game = await load_game(game_type, int(game_id_text))
    await render_game_message(callback, game_type, game)
    await callback.answer("Bekor qilindi.")


@router.callback_query(F.data.startswith("bg:resign_yes:"))
async def resign_confirm(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    game = await load_game(game_type, int(game_id_text))
    user_color = color_for_user(game, callback.from_user.id)
    if not user_color:
        await callback.answer("Bu sizning o'yiningiz emas.", show_alert=True)
        return
    if game.status not in ACTIVE_STATUSES:
        await callback.answer("O'yin tugagan.", show_alert=True)
        return

    await finish_game(game_type, game, other_color(user_color), "resign")
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game, result_button_text(game))
    await callback.answer("Taslim bo'ldingiz.")


@router.callback_query(F.data.startswith("bg:draw:"))
async def draw_offer(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    game = await load_game(game_type, int(game_id_text))
    user_color = color_for_user(game, callback.from_user.id)
    if not user_color:
        await callback.answer("Bu sizning o'yiningiz emas.", show_alert=True)
        return
    if game.status not in ACTIVE_STATUSES:
        await callback.answer("O'yin tugagan.", show_alert=True)
        return

    game.draw_offered_by = player_for_color(game, user_color)
    await game.save()
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game)
    await callback.answer("Durang taklif qilindi.")


@router.callback_query(F.data.startswith("bg:draw_no:"))
async def draw_reject(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    game = await load_game(game_type, int(game_id_text))
    user_color = color_for_user(game, callback.from_user.id)
    if not user_color or not game.draw_offered_by_id:
        await callback.answer("Durang taklifi yo'q.", show_alert=True)
        return
    if game.draw_offered_by.user_id == callback.from_user.id:
        await callback.answer("Taklifga faqat raqib javob beradi.", show_alert=True)
        return
    game.draw_offered_by = None
    await game.save()
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game)
    await callback.answer("Durang rad etildi.")


@router.callback_query(F.data.startswith("bg:draw_yes:"))
async def draw_accept(callback: CallbackQuery):
    _, _, game_type, game_id_text = callback.data.split(":")
    game = await load_game(game_type, int(game_id_text))
    if not game.draw_offered_by_id:
        await callback.answer("Durang taklifi yo'q.", show_alert=True)
        return
    if game.draw_offered_by.user_id == callback.from_user.id:
        await callback.answer("Taklifga faqat raqib javob beradi.", show_alert=True)
        return
    if not color_for_user(game, callback.from_user.id):
        await callback.answer("Bu sizning o'yiningiz emas.", show_alert=True)
        return

    await finish_game(game_type, game, None, "draw")
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game, result_button_text(game))
    await callback.answer("Durang qabul qilindi.")
