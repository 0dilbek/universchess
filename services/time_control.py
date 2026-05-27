from datetime import datetime, timezone


INCREMENTS = {
    10: 5,
    15: 10,
    30: 20,
    60: 30,
}


def initial_seconds(minutes: int) -> int:
    return minutes * 60


def increment_for(minutes: int) -> int:
    return INCREMENTS.get(minutes, 0)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def elapsed_since(value: datetime | None, now: datetime | None = None) -> int:
    if not value:
        return 0
    now = now or utc_now()
    value = normalize_datetime(value)
    return max(0, int((now - value).total_seconds()))


def current_time_left(game, color: str, now: datetime | None = None) -> int:
    stored = game.white_time_left if color == "white" else game.black_time_left
    if game.status != "active" or game.turn != color:
        return stored
    return stored - elapsed_since(game.last_move_at, now)


def timed_out_color(game, now: datetime | None = None) -> str | None:
    if game.status != "active":
        return None
    if current_time_left(game, game.turn, now) <= 0:
        return game.turn
    return None


def apply_clock(game, mover_color: str, now: datetime | None = None) -> bool:
    now = now or utc_now()
    if not game.last_move_at:
        game.last_move_at = now
        return True

    elapsed = elapsed_since(game.last_move_at, now)
    if mover_color == "white":
        game.white_time_left -= elapsed
        timed_out = game.white_time_left <= 0
        if not timed_out:
            game.white_time_left += game.increment_seconds
    else:
        game.black_time_left -= elapsed
        timed_out = game.black_time_left <= 0
        if not timed_out:
            game.black_time_left += game.increment_seconds

    game.last_move_at = now
    return not timed_out


def clock_text(seconds: int) -> str:
    seconds = max(0, seconds)
    minutes, sec = divmod(seconds, 60)
    return f"{minutes:02d}:{sec:02d}"
