from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from models.board_game import ChessProfile
from services.profile_stats import sync_total_profile_stats
from services.telegram_safe import answer_message
from services.users import user_mention

router = Router()


def medal(index: int) -> str:
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(index, f"{index}.")


@router.message(Command("top", "chess_top"))
async def top_handler(message: Message):
    profiles = await ChessProfile.all().prefetch_related("user")
    rows = []
    for profile in profiles:
        stats = await sync_total_profile_stats(profile.user)
        rows.append((profile.user, stats))

    rows.sort(key=lambda row: (-row[1]["rating"], -row[1]["wins"], row[1]["losses"]))
    rows = rows[:10]

    if not rows:
        await answer_message(message, "Hali reyting statistikasi yo'q.")
        return

    lines = ["🏆 Reyting bo'yicha TOP\n"]
    for index, (user, stats) in enumerate(rows, start=1):
        lines.append(
            f"{medal(index)} {user_mention(user)}\n"
            f"⭐️ {stats['rating']} | 🎮 {stats['games_count']} | ✅ {stats['wins']} | 💜 {stats['losses']} | 🤝 {stats['draws']}"
        )

    await answer_message(message, "\n\n".join(lines))
