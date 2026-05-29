import chess
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from models.board_game import CheckersGame, ChessGame
from services import checkers
from services.telegram_safe import edit_bot_message_text, edit_message_text
from services.time_control import clock_text, current_time_left
from services.users import user_mention

CHESS_PIECES = {
    "P": "⚪♙",
    "N": "⚪♘",
    "B": "⚪♗",
    "R": "⚪♖",
    "Q": "⚪♕",
    "K": "⚪♔",
    "p": "⚫♟",
    "n": "⚫♞",
    "b": "⚫♝",
    "r": "⚫♜",
    "q": "⚫♛",
    "k": "⚫♚",
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


def chess_square_style(square: chess.Square) -> str:
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)
    return "success" if (file_index + rank_index) % 2 else "danger"


def chess_square_text(board: chess.Board, square: chess.Square, square_name: str, selected: str | None, targets: set[str]) -> str:
    piece = board.piece_at(square)
    base = CHESS_PIECES[piece.symbol()] if piece else "•" if square_name in targets else " "
    if square_name == selected:
        return f"🔸{base}"
    return base


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
        text=chess_square_text(board, square, name, selected, targets),
        callback_data=callback,
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


def checkers_square_text(
    piece: str | None,
    square: str,
    selected: str | None,
) -> str:
    base = CHECKERS_PIECES.get(piece, " ")
    if square == selected:
        return f"🔸{base}"
    return base


def checkers_keyboard(game: CheckersGame, result_text: str | None = None):
    board = dict(game.board_state)
    keyboard = InlineKeyboardBuilder()
    selected = game.selected_square
    all_legal = checkers.legal_moves(board, game.turn, game.forced_square)
    legal = [move for move in all_legal if selected and move["from"] == selected]
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
                text=checkers_square_text(piece, square, selected),
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
        f"⚪ {white}  {clock_text(current_time_left(game, 'white'))}\n"
        f"⚫ {black}  {clock_text(current_time_left(game, 'black'))}\n"
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
    if callback.inline_message_id:
        await edit_bot_message_text(
            callback.bot,
            inline_message_id=callback.inline_message_id,
            text=text,
            reply_markup=markup,
        )
    else:
        await edit_message_text(callback.message, text, reply_markup=markup)


def game_markup(game_type: str, game, result_text: str | None = None):
    return chess_keyboard(game, result_text) if game_type == "chess" else checkers_keyboard(game, result_text)
