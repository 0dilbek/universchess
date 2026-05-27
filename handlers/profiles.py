from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from models.board_game import ChessProfile
from models.user import Profile
from services.users import get_or_create_user, user_mention

router = Router()


def percent(part: int, total: int) -> str:
    if total <= 0:
        return "0%"
    return f"{part * 100 / total:.1f}%"


@router.message(Command("profile"))
async def profile_handler(message: Message):
    user = await get_or_create_user(message.from_user)
    profile = await Profile.get(user=user)
    chess_profile = await ChessProfile.get(user=user)

    await message.answer(
        f"👤 {user_mention(user)}\n\n"
        f"💵 Dollar: {profile.dollar}\n"
        f"💎 Olmos: {profile.diamond}\n\n"
        "♟ Shaxmat profili\n"
        f"Reyting: {chess_profile.rating}\n"
        f"O'yinlar: {chess_profile.games_count}\n"
        f"G'alabalar: {chess_profile.wins}\n"
        f"Mag'lubiyatlar: {chess_profile.losses}\n"
        f"Duranglar: {chess_profile.draws}\n"
        f"Winrate: {percent(chess_profile.wins, chess_profile.games_count)}"
    )
