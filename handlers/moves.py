import chess
from aiogram import F, Router
from aiogram.types import CallbackQuery

from constants import ACTIVE_STATUSES
from keyboards.board import render_game_message
from models.board_game import CheckersGame, CheckersMove, ChessGame, ChessMove
from services import checkers
from services.game_state import color_for_user, finish_game, load_game, other_color, player_for_color, result_button_text
from services.time_control import apply_clock

router = Router()


@router.callback_query(F.data.startswith("bg:sel:"))
async def select_square(callback: CallbackQuery):
    _, _, game_type, game_id_text, square = callback.data.split(":")
    game = await load_game(game_type, int(game_id_text))
    if game.status not in ACTIVE_STATUSES:
        await callback.answer("O'yin tugagan.", show_alert=True)
        return

    user_color = color_for_user(game, callback.from_user.id)
    if not user_color:
        await callback.answer("Bu sizning o'yiningiz emas.", show_alert=True)
        return
    if user_color != game.turn:
        await callback.answer("Hozir sizning navbatingiz emas.", show_alert=True)
        return

    if game_type == "chess":
        board = chess.Board(game.fen)
        piece = board.piece_at(chess.parse_square(square))
        if not piece or ("white" if piece.color == chess.WHITE else "black") != user_color:
            await callback.answer("O'z donangizni tanlang.", show_alert=True)
            return
    else:
        board = dict(game.board_state)
        piece = board.get(square)
        if game.forced_square and square != game.forced_square:
            await callback.answer("Ko'p urishni shu dona bilan davom ettiring.", show_alert=True)
            return
        if not piece or checkers.color_of(piece) != user_color:
            await callback.answer("O'z donangizni tanlang.", show_alert=True)
            return
        if not checkers.legal_moves_for_square(board, user_color, square, game.forced_square):
            await callback.answer("Bu dona yura olmaydi.", show_alert=True)
            return

    game.selected_square = square
    await game.save()
    game = await load_game(game_type, game.id)
    await render_game_message(callback, game_type, game)
    await callback.answer()


@router.callback_query(F.data.startswith("bg:move:"))
async def move_piece(callback: CallbackQuery):
    _, _, game_type, game_id_text, from_square, to_square = callback.data.split(":")
    game = await load_game(game_type, int(game_id_text))
    if game.status not in ACTIVE_STATUSES:
        await callback.answer("O'yin tugagan.", show_alert=True)
        return

    user_color = color_for_user(game, callback.from_user.id)
    if user_color != game.turn:
        await callback.answer("Hozir sizning navbatingiz emas.", show_alert=True)
        return

    if not apply_clock(game, user_color):
        await finish_game(game_type, game, other_color(user_color), "timeout")
        game = await load_game(game_type, game.id)
        await render_game_message(callback, game_type, game, result_button_text(game))
        await callback.answer("Vaqt tugadi.", show_alert=True)
        return

    if game_type == "chess":
        await handle_chess_move(callback, game, user_color, from_square, to_square)
    else:
        await handle_checkers_move(callback, game, user_color, from_square, to_square)


async def handle_chess_move(callback: CallbackQuery, game: ChessGame, user_color: str, from_square: str, to_square: str):
    board = chess.Board(game.fen)
    move_text = from_square + to_square
    piece = board.piece_at(chess.parse_square(from_square))
    if piece and piece.piece_type == chess.PAWN and to_square[1] in {"1", "8"}:
        move_text += "q"
    move = chess.Move.from_uci(move_text)
    if move not in board.legal_moves:
        await callback.answer("Bu yurish mumkin emas.", show_alert=True)
        return

    san = board.san(move)
    board.push(move)
    move_count = await ChessMove.filter(game=game).count() + 1
    await ChessMove.create(
        game=game,
        player=player_for_color(game, user_color),
        move_number=move_count,
        from_square=from_square,
        to_square=to_square,
        promotion=move.promotion and chess.piece_symbol(move.promotion),
        san=san,
        fen_after=board.fen(),
    )

    game.fen = board.fen()
    game.turn = other_color(user_color)
    game.selected_square = None
    game.draw_offered_by = None

    if board.is_checkmate():
        await finish_game("chess", game, user_color, "checkmate")
    elif board.is_stalemate():
        await finish_game("chess", game, None, "stalemate")
    elif board.is_insufficient_material():
        await finish_game("chess", game, None, "insufficient_material")
    else:
        await game.save()

    game = await load_game("chess", game.id)
    await render_game_message(callback, "chess", game, result_button_text(game) if game.status != "active" else None)
    await callback.answer()


async def handle_checkers_move(callback: CallbackQuery, game: CheckersGame, user_color: str, from_square: str, to_square: str):
    board = dict(game.board_state)
    legal = checkers.legal_moves_for_square(board, user_color, from_square, game.forced_square)
    move = next((item for item in legal if item["to"] == to_square), None)
    if not move:
        await callback.answer("Bu yurish mumkin emas.", show_alert=True)
        return

    next_board, became_king = checkers.apply_move(board, move)
    move_count = await CheckersMove.filter(game=game).count() + 1
    await CheckersMove.create(
        game=game,
        player=player_for_color(game, user_color),
        move_number=move_count,
        from_square=from_square,
        to_square=to_square,
        captured_squares=move["captured"],
        became_king=became_king,
        board_after=next_board,
    )

    game.board_state = next_board
    game.selected_square = None
    game.draw_offered_by = None
    if move["captured"] and checkers.captures_from(next_board, to_square):
        game.forced_square = to_square
    else:
        game.forced_square = None
        game.turn = other_color(user_color)

    winner, reason = checkers.winner_after(next_board, game.turn)
    if winner:
        await finish_game("checkers", game, winner, reason)
    else:
        await game.save()

    game = await load_game("checkers", game.id)
    await render_game_message(callback, "checkers", game, result_button_text(game) if game.status != "active" else None)
    await callback.answer()
