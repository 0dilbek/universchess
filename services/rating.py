def elo_delta(winner_rating: int, loser_rating: int, result: float, k: int = 32) -> int:
    expected = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    return round(k * (result - expected))


def win_loss_ratings(winner_rating: int, loser_rating: int) -> tuple[int, int]:
    delta = elo_delta(winner_rating, loser_rating, 1)
    return winner_rating + delta, max(100, loser_rating - delta)


def draw_ratings(first_rating: int, second_rating: int) -> tuple[int, int]:
    first_delta = elo_delta(first_rating, second_rating, 0.5)
    second_delta = elo_delta(second_rating, first_rating, 0.5)
    return max(100, first_rating + first_delta), max(100, second_rating + second_delta)


def reward_for(reason: str, winner_rating: int, loser_rating: int, move_count: int) -> int:
    if reason == "resign":
        base = 20
    elif reason in {"checkmate", "capture_all", "blocked"}:
        base = 50
    elif reason == "timeout":
        base = 30
    else:
        base = 30

    rating_bonus = max(0, min(30, (loser_rating - winner_rating) // 20))
    length_bonus = 0
    if 15 <= move_count < 40:
        length_bonus = 10
    elif move_count >= 40:
        length_bonus = 20

    return min(100, max(10, base + rating_bonus + length_bonus))
