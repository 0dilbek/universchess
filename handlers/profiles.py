from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from models.user import Profile
from services.profile_stats import sync_chess_profile_stats
from services.telegram_safe import answer_message
from services.users import get_or_create_user, user_mention

router = Router()
MAFIA_BOT_URL = "https://t.me/UnvMafiaBot"


def percent(part: int, total: int) -> str:
    if total <= 0:
        return "0%"
    return f"{part * 100 / total:.1f}%"


def profile_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🎭 Mafia o'yini", url=MAFIA_BOT_URL)
    return keyboard.as_markup()


@router.message(Command("profile"))
async def profile_handler(message: Message):
    user = await get_or_create_user(message.from_user)
    profile = await Profile.get(user=user)
    chess_profile = await sync_chess_profile_stats(user)

    await answer_message(
        message,
        f"👤 {user_mention(user)}\n\n"
        f"💵 Dollar: {profile.dollar}\n"
        f"💎 Olmos: {profile.diamond}\n\n"
        f"🏆 Reyting: {chess_profile.rating}\n"
        f"🎮 O'yinlar: {chess_profile.games_count}\n"
        f"✅ G'alabalar: {chess_profile.wins}\n"
        f"❌ Mag'lubiyatlar: {chess_profile.losses}\n"
        f"🤝 Duranglar: {chess_profile.draws}\n"
        f"📈 Winrate: {percent(chess_profile.wins, chess_profile.games_count)}",
        reply_markup=profile_keyboard(),
    )
