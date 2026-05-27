from asyncio import Lock
from contextlib import asynccontextmanager

_locks: dict[tuple[str, int], Lock] = {}
_snapshots: dict[tuple[str, int], dict] = {}


def game_key(game_type: str, game_id: int) -> tuple[str, int]:
    return game_type, int(game_id)


def game_lock(game_type: str, game_id: int) -> Lock:
    key = game_key(game_type, game_id)
    if key not in _locks:
        _locks[key] = Lock()
    return _locks[key]


@asynccontextmanager
async def locked_game(game_type: str, game_id: int):
    lock = game_lock(game_type, game_id)
    async with lock:
        yield


def remember_game(game_type: str, game) -> None:
    _snapshots[game_key(game_type, game.id)] = {
        "status": game.status,
        "turn": game.turn,
        "white_time_left": game.white_time_left,
        "black_time_left": game.black_time_left,
        "selected_square": game.selected_square,
    }


def forget_game(game_type: str, game_id: int) -> None:
    _snapshots.pop(game_key(game_type, game_id), None)
