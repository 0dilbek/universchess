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


def apply_clock(game, mover_color: str, now: datetime | None = None) -> bool:
    now = now or utc_now()
    if not game.last_move_at:
        game.last_move_at = now
        return True

    elapsed = max(0, int((now - game.last_move_at).total_seconds()))
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
