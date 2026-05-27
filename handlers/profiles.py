from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from models.user import Profile
from services.profile_stats import sync_total_profile_stats
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
    game_stats = await sync_total_profile_stats(user)

    await answer_message(
        message,
        f"""👤 {user_mention(user)}\n\n"""
        f"""<tg-emoji emoji-id="5215239948420003628">💵</tg-emoji> Dollar: {profile.dollar}\n"""
        f"""<tg-emoji emoji-id="5229173741451230931">💎</tg-emoji> Olmos: {profile.diamond}\n\n"""
        f"""<tg-emoji emoji-id="5287722392032919843">💰</tg-emoji> Winrate: {percent(game_stats["wins"], game_stats["games_count"])}\n"""
        f"""<tg-emoji emoji-id="5323386314400211783">✅</tg-emoji> G'alabalar: {game_stats["wins"]}\n"""
        f"""<tg-emoji emoji-id="5332517603850074848">🤝</tg-emoji> Duranglar: {game_stats["draws"]}\n"""
        f"""<tg-emoji emoji-id="5460936902662168397">💜</tg-emoji> Mag'lubiyatlar: {game_stats["losses"]}\n\n"""
        f"""<tg-emoji emoji-id="5251332925135283922">⭐️</tg-emoji> Reyting: {game_stats["rating"]}\n"""
        f"""<tg-emoji emoji-id="5210768496622840660">🎮</tg-emoji> O'yinlar: {game_stats["games_count"]}""",
        reply_markup=profile_keyboard(),
        parse_mode="HTML",
    )
