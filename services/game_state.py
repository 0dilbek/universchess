from models.board_game import CheckersGame, CheckersMove, CheckersProfile, ChessGame, ChessMove, ChessProfile
from models.user import Profile
from services.rating import draw_ratings, reward_for, win_loss_ratings
from services.time_control import utc_now


def other_color(color: str) -> str:
    return "black" if color == "white" else "white"


def player_for_color(game, color: str):
    return game.white_player if color == "white" else game.black_player


def color_for_user(game, user_id: int) -> str | None:
    if game.white_player.user_id == user_id:
        return "white"
    if game.black_player.user_id == user_id:
        return "black"
    return None


async def load_game(game_type: str, game_id: int):
    model = ChessGame if game_type == "chess" else CheckersGame
    return await model.get(id=game_id).prefetch_related("white_player", "black_player", "winner", "draw_offered_by")


async def finish_game(game_type: str, game, winner_color: str | None, reason: str):
    now = utc_now()
    game.result_reason = reason
    game.finished_at = now
    game.draw_offered_by = None
    game.selected_square = None
    if hasattr(game, "forced_square"):
        game.forced_square = None

    profile_model = ChessProfile if game_type == "chess" else CheckersProfile
    move_model = ChessMove if game_type == "chess" else CheckersMove
    white_profile = await profile_model.get(user=game.white_player)
    black_profile = await profile_model.get(user=game.black_player)
    move_count = await move_model.filter(game=game).count()

    white_profile.games_count += 1
    black_profile.games_count += 1

    if winner_color is None:
        game.status = "draw"
        white_profile.draws += 1
        black_profile.draws += 1
        white_profile.rating, black_profile.rating = draw_ratings(white_profile.rating, black_profile.rating)
        game.reward_amount = 0
    else:
        winner = player_for_color(game, winner_color)
        game.winner = winner
        game.status = f"{winner_color}_won"

        winner_profile = white_profile if winner_color == "white" else black_profile
        loser_profile = black_profile if winner_color == "white" else white_profile
        winner_profile.wins += 1
        loser_profile.losses += 1
        winner_profile.rating, loser_profile.rating = win_loss_ratings(winner_profile.rating, loser_profile.rating)
        game.reward_amount = reward_for(reason, winner_profile.rating, loser_profile.rating, move_count)

        main_profile = await Profile.get(user=winner)
        main_profile.dollar += game.reward_amount
        await main_profile.save()

    await white_profile.save()
    await black_profile.save()
    await game.save()


def result_button_text(game) -> str:
    reason = game.result_reason or "finished"
    if game.status == "draw":
        return f"🤝 Durang ({reason})"
    if game.status == "white_won":
        return f"⚪ G'olib ({reason})"
    if game.status == "black_won":
        return f"⚫ G'olib ({reason})"
    return f"✅ Tugadi ({reason})"
