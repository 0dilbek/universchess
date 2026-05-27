FILES = "abcdefgh"
RANKS = "12345678"


def initial_board() -> dict[str, str]:
    board = {}
    for rank in range(1, 9):
        for file_index, file_name in enumerate(FILES):
            if (file_index + rank) % 2 == 0:
                square = f"{file_name}{rank}"
                if rank <= 3:
                    board[square] = "w"
                elif rank >= 6:
                    board[square] = "b"
    return board


def color_of(piece: str) -> str:
    return "white" if piece.lower() == "w" else "black"


def is_king(piece: str) -> bool:
    return piece.isupper()


def square_to_coords(square: str) -> tuple[int, int]:
    return FILES.index(square[0]), RANKS.index(square[1])


def coords_to_square(file_index: int, rank_index: int) -> str | None:
    if 0 <= file_index < 8 and 0 <= rank_index < 8:
        return f"{FILES[file_index]}{RANKS[rank_index]}"
    return None


def move_dirs(piece: str, captures: bool = False) -> list[tuple[int, int]]:
    if is_king(piece):
        dirs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
    elif color_of(piece) == "white":
        dirs = [(1, 1), (-1, 1)]
    else:
        dirs = [(1, -1), (-1, -1)]
    if captures:
        return [(df * 2, dr * 2) for df, dr in dirs]
    return dirs


def pieces_for(board: dict[str, str], color: str) -> list[str]:
    return [square for square, piece in board.items() if color_of(piece) == color]


def captures_from(board: dict[str, str], square: str) -> list[dict]:
    piece = board.get(square)
    if not piece:
        return []

    file_index, rank_index = square_to_coords(square)
    moves = []
    for df, dr in move_dirs(piece, captures=True):
        mid = coords_to_square(file_index + df // 2, rank_index + dr // 2)
        target = coords_to_square(file_index + df, rank_index + dr)
        if not mid or not target or target in board:
            continue
        captured = board.get(mid)
        if captured and color_of(captured) != color_of(piece):
            moves.append({"from": square, "to": target, "captured": [mid]})
    return moves


def simple_moves_from(board: dict[str, str], square: str) -> list[dict]:
    piece = board.get(square)
    if not piece:
        return []

    file_index, rank_index = square_to_coords(square)
    moves = []
    for df, dr in move_dirs(piece):
        target = coords_to_square(file_index + df, rank_index + dr)
        if target and target not in board:
            moves.append({"from": square, "to": target, "captured": []})
    return moves


def legal_moves(board: dict[str, str], color: str, forced_square: str | None = None) -> list[dict]:
    squares = [forced_square] if forced_square else pieces_for(board, color)
    capture_moves = []
    for square in squares:
        if square:
            capture_moves.extend(captures_from(board, square))
    if capture_moves:
        return capture_moves

    if forced_square:
        return []

    moves = []
    for square in squares:
        moves.extend(simple_moves_from(board, square))
    return moves


def legal_moves_for_square(board: dict[str, str], color: str, square: str, forced_square: str | None = None) -> list[dict]:
    return [move for move in legal_moves(board, color, forced_square) if move["from"] == square]


def apply_move(board: dict[str, str], move: dict) -> tuple[dict[str, str], bool]:
    next_board = dict(board)
    piece = next_board.pop(move["from"])
    for captured in move["captured"]:
        next_board.pop(captured, None)

    became_king = False
    target_rank = move["to"][1]
    if piece == "w" and target_rank == "8":
        piece = "W"
        became_king = True
    elif piece == "b" and target_rank == "1":
        piece = "B"
        became_king = True

    next_board[move["to"]] = piece
    return next_board, became_king


def winner_after(board: dict[str, str], next_turn: str) -> tuple[str | None, str | None]:
    white_pieces = pieces_for(board, "white")
    black_pieces = pieces_for(board, "black")
    if not white_pieces:
        return "black", "capture_all"
    if not black_pieces:
        return "white", "capture_all"
    if not legal_moves(board, next_turn):
        return ("black" if next_turn == "white" else "white"), "blocked"
    return None, None
