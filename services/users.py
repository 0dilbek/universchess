from tortoise.expressions import Q

from constants import ACTIVE_STATUSES
from models.board_game import CheckersGame, CheckersProfile, ChessGame, ChessProfile
from models.user import Profile, User


def user_mention(user: User) -> str:
    return user.full_name or user.mention or str(user.user_id)


async def get_or_create_user(tg_user) -> User:
    full_name = tg_user.full_name or tg_user.first_name or ""
    user, _ = await User.get_or_create(
        user_id=tg_user.id,
        defaults={
            "full_name": full_name,
            "is_bot": tg_user.is_bot,
            "mention": full_name,
        },
    )
    changed = False
    if user.full_name != full_name:
        user.full_name = full_name
        changed = True
    if user.is_bot != tg_user.is_bot:
        user.is_bot = tg_user.is_bot
        changed = True
    if changed:
        await user.save()

    await Profile.get_or_create(user=user)
    await ChessProfile.get_or_create(user=user)
    await CheckersProfile.get_or_create(user=user)
    return user


async def active_games_count(user: User) -> int:
    chess_count = await ChessGame.filter(
        Q(white_player=user) | Q(black_player=user),
        status__in=ACTIVE_STATUSES,
    ).count()
    checkers_count = await CheckersGame.filter(
        Q(white_player=user) | Q(black_player=user),
        status__in=ACTIVE_STATUSES,
    ).count()
    return chess_count + checkers_count
