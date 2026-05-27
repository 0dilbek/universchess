from tortoise.expressions import Q

from models.board_game import ChessGame, ChessProfile
from models.user import User

FINISHED_CHESS_STATUSES = ["white_won", "black_won", "draw"]
DECISIVE_CHESS_STATUSES = ["white_won", "black_won"]


async def sync_chess_profile_stats(user: User) -> ChessProfile:
    chess_profile = await ChessProfile.get(user=user)
    player_filter = Q(white_player=user) | Q(black_player=user)

    wins = await ChessGame.filter(player_filter, winner=user).count()
    decisive_games = await ChessGame.filter(player_filter, status__in=DECISIVE_CHESS_STATUSES).count()
    draws = await ChessGame.filter(player_filter, status="draw").count()

    chess_profile.wins = wins
    chess_profile.losses = max(0, decisive_games - wins)
    chess_profile.draws = draws
    chess_profile.games_count = await ChessGame.filter(player_filter, status__in=FINISHED_CHESS_STATUSES).count()
    await chess_profile.save()
    return chess_profile
