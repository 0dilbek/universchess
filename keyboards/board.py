import chess
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ShaxmatEmojies
from models.board_game import CheckersGame, ChessGame
from services import checkers
from services.time_control import clock_text
from services.users import user_mention

CHESS_PIECES = {
    "P": ShaxmatEmojies.WHITE_PIYODA,
    "N": ShaxmatEmojies.WHITE_OT,
    "B": ShaxmatEmojies.WHITE_FIL,
    "R": ShaxmatEmojies.WHITE_RUH,
    "Q": ShaxmatEmojies.WHITE_FARZIN,
    "K": ShaxmatEmojies.WHITE_QIROL,
    "p": ShaxmatEmojies.BLACK_PIYODA,
    "n": ShaxmatEmojies.BLACK_OT,
    "b": ShaxmatEmojies.BLACK_FIL,
    "r": ShaxmatEmojies.BLACK_RUH,
    "q": ShaxmatEmojies.BLACK_FARZIN,
    "k": ShaxmatEmojies.BLACK_QIROL,
}
CHECKERS_PIECES = {"w": "⚪", "W": "👑", "b": "⚫", "B": "♛"}


def action_buttons(keyboard: InlineKeyboardBuilder, game_type: str, game_id: int, game, result_text: str | None = None):
    if result_text:
        keyboard.button(text=result_text, callback_data="bg:noop")
        keyboard.adjust(*([8] * 8), 1)
        return

    if game.draw_offered_by_id:
        keyboard.button(text="✅ Durang", callback_data=f"bg:draw_yes:{game_type}:{game_id}")
        keyboard.button(text="❌ Rad etish", callback_data=f"bg:draw_no:{game_type}:{game_id}")
    else:
        keyboard.button(text="🏳️ Taslim bo'lish", callback_data=f"bg:resign:{game_type}:{game_id}")
        keyboard.button(text="🤝 Durang taklif", callback_data=f"bg:draw:{game_type}:{game_id}")
    keyboard.adjust(*([8] * 8), 2)


def resign_confirm_keyboard(game_type: str, game_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Tasdiqlash", callback_data=f"bg:resign_yes:{game_type}:{game_id}")
    keyboard.button(text="❌ Qaytish", callback_data=f"bg:resign_no:{game_type}:{game_id}")
    keyboard.adjust(2)
    return keyboard.as_markup()


def chess_square_style(square: chess.Square) -> str:
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)
    return "success" if (file_index + rank_index) % 2 else "danger"


def chess_square_text(square_name: str, selected: str | None, targets: set[str]) -> str:
    if square_name == selected:
        return "🔸"
    if square_name in targets:
        return "🔹"
    return " "


def chess_piece_icon(board: chess.Board, square: chess.Square) -> str | None:
    piece = board.piece_at(square)
    if not piece:
        return None
    return str(CHESS_PIECES[piece.symbol()])


def add_chess_square_button(
    keyboard: InlineKeyboardBuilder,
    board: chess.Board,
    square: chess.Square,
    selected: str | None,
    targets: set[str],
    callback: str,
) -> None:
    name = chess.square_name(square)
    keyboard.button(
        text=chess_square_text(name, selected, targets),
        callback_data=callback,
        icon_custom_emoji_id=chess_piece_icon(board, square),
        style=chess_square_style(square),
    )


def chess_keyboard(game: ChessGame, result_text: str | None = None):
    board = chess.Board(game.fen)
    keyboard = InlineKeyboardBuilder()
    selected = game.selected_square
    targets = {
        chess.square_name(move.to_square)
        for move in board.legal_moves
        if selected and chess.square_name(move.from_square) == selected
    }

    for rank in range(7, -1, -1):
        for file_index in range(8):
            square = chess.square(file_index, rank)
            name = chess.square_name(square)
            if selected and name in targets:
                callback = f"bg:move:chess:{game.id}:{selected}:{name}"
            else:
                callback = f"bg:sel:chess:{game.id}:{name}"
            add_chess_square_button(keyboard, board, square, selected, targets, callback)
    action_buttons(keyboard, "chess", game.id, game, result_text)
    return keyboard.as_markup()


def checkers_square_style(file_index: int, rank: int) -> str:
    return "success" if (file_index + rank) % 2 else "danger"


def checkers_square_text(piece: str | None, square: str, selected: str | None, targets: set[str]) -> str:
    base = CHECKERS_PIECES.get(piece, " ")
    if square == selected:
        return f"🔸{base}"
    if square in targets:
        return f"🔹{base}"
    return base


def checkers_keyboard(game: CheckersGame, result_text: str | None = None):
    board = dict(game.board_state)
    keyboard = InlineKeyboardBuilder()
    selected = game.selected_square
    legal = checkers.legal_moves_for_square(board, game.turn, selected, game.forced_square) if selected else []
    targets = {move["to"] for move in legal}

    for rank in range(7, -1, -1):
        for file_index, file_name in enumerate(checkers.FILES):
            square = f"{file_name}{checkers.RANKS[rank]}"
            piece = board.get(square)
            if selected and square in targets:
                callback = f"bg:move:checkers:{game.id}:{selected}:{square}"
            else:
                callback = f"bg:sel:checkers:{game.id}:{square}"
            keyboard.button(
                text=checkers_square_text(piece, square, selected, targets),
                callback_data=callback,
                style=checkers_square_style(file_index, rank),
            )
    action_buttons(keyboard, "checkers", game.id, game, result_text)
    return keyboard.as_markup()


def status_line(game) -> str:
    white = user_mention(game.white_player)
    black = user_mention(game.black_player)
    turn = "Oq" if game.turn == "white" else "Qora"
    return (
        f"⚪ {white}  {clock_text(game.white_time_left)}\n"
        f"⚫ {black}  {clock_text(game.black_time_left)}\n"
        f"Navbat: {turn}"
    )


def game_text(game_type: str, game) -> str:
    title = "♟ Shaxmat" if game_type == "chess" else "⚫ Shashka"
    return f"{title}\n\n{status_line(game)}"


async def render_game_message(callback: CallbackQuery, game_type: str, game, result_text: str | None = None):
    markup = chess_keyboard(game, result_text) if game_type == "chess" else checkers_keyboard(game, result_text)
    text = game_text(game_type, game)
    if result_text:
        text = f"{text}\n\n{result_text}"
    await callback.message.edit_text(text, reply_markup=markup)
