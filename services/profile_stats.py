from tortoise.expressions import Q

from models.board_game import CheckersGame, CheckersProfile, ChessGame, ChessProfile
from models.user import User


def count_games(games: list, user: User) -> dict[str, int]:
    wins = 0
    losses = 0
    draws = 0

    for game in games:
        if game.status == "active" or game.status == "cancelled":
            continue
        if game.winner_id:
            if game.winner_id == user.id:
                wins += 1
            else:
                losses += 1
        elif game.status == "draw":
            draws += 1

    return {
        "games_count": wins + losses + draws,
        "wins": wins,
        "losses": losses,
        "draws": draws,
    }


async def sync_chess_profile_stats(user: User) -> ChessProfile:
    chess_profile = await ChessProfile.get(user=user)
    player_filter = Q(white_player=user) | Q(black_player=user)
    games = await ChessGame.filter(player_filter)
    stats = count_games(games, user)

    chess_profile.wins = stats["wins"]
    chess_profile.losses = stats["losses"]
    chess_profile.draws = stats["draws"]
    chess_profile.games_count = stats["games_count"]
    await chess_profile.save()
    return chess_profile


async def sync_checkers_profile_stats(user: User) -> CheckersProfile:
    checkers_profile = await CheckersProfile.get(user=user)
    player_filter = Q(white_player=user) | Q(black_player=user)
    games = await CheckersGame.filter(player_filter)
    stats = count_games(games, user)

    checkers_profile.wins = stats["wins"]
    checkers_profile.losses = stats["losses"]
    checkers_profile.draws = stats["draws"]
    checkers_profile.games_count = stats["games_count"]
    await checkers_profile.save()
    return checkers_profile


async def sync_total_profile_stats(user: User) -> dict[str, int]:
    chess_profile = await sync_chess_profile_stats(user)
    checkers_profile = await sync_checkers_profile_stats(user)

    games_count = chess_profile.games_count + checkers_profile.games_count
    wins = chess_profile.wins + checkers_profile.wins
    losses = chess_profile.losses + checkers_profile.losses
    draws = chess_profile.draws + checkers_profile.draws
    rating_weight = chess_profile.games_count + checkers_profile.games_count
    if rating_weight:
        rating = round(
            (
                chess_profile.rating * chess_profile.games_count
                + checkers_profile.rating * checkers_profile.games_count
            )
            / rating_weight
        )
    else:
        rating = chess_profile.rating

    return {
        "rating": rating,
        "games_count": games_count,
        "wins": wins,
        "losses": losses,
        "draws": draws,
    }


async def sync_all_chess_profile_stats() -> None:
    profiles = await ChessProfile.all().prefetch_related("user")
    for profile in profiles:
        await sync_chess_profile_stats(profile.user)
