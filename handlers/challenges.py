from secrets import token_hex

import chess
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.board import checkers_keyboard, chess_keyboard, game_text
from keyboards.challenge import accept_keyboard, challenge_time_keyboard, challenge_type_keyboard
from models.board_game import CheckersGame, ChessGame
from models.user import User
from services import checkers
from services.time_control import increment_for, initial_seconds, utc_now
from services.users import active_games_count, get_or_create_user, user_mention

router = Router()
PENDING_CHALLENGES: dict[str, dict] = {}


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Univers Chess.\n\n"
        "Guruhda /chesswhite yoki /chessblack yozing, keyin shaxmat yoki shashkani tanlang."
    )


@router.message(Command("chesswhite", "chessblack", "chessbalck"))
async def create_challenge(message: Message):
    if message.chat.type == "private":
        await message.answer("Lichkada o'yin boshlash keyingi feature. Hozircha guruhda ishlaydi.")
        return

    creator = await get_or_create_user(message.from_user)
    if await active_games_count(creator) >= 2:
        await message.answer("Sizda active o'yinlar soni 2 taga yetgan.")
        return

    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.answer("Bot bilan o'yin yaratib bo'lmaydi.")
            return
        if message.reply_to_message.from_user.id == message.from_user.id:
            await message.answer("O'zingizga qarshi o'ynay olmaysiz.")
            return
        target = await get_or_create_user(message.reply_to_message.from_user)

    command = (message.text or "").split()[0].lower()
    creator_color = "white" if command == "/chesswhite" else "black"
    challenge_id = token_hex(3)
    PENDING_CHALLENGES[challenge_id] = {
        "creator_id": creator.id,
        "creator_tg_id": creator.user_id,
        "creator_name": user_mention(creator),
        "creator_color": creator_color,
        "target_tg_id": target.user_id if target else None,
        "target_name": user_mention(target) if target else None,
        "chat_id": message.chat.id,
        "chat_type": message.chat.type,
    }

    color_text = "oq" if creator_color == "white" else "qora"
    target_text = f"\nRaqib: {user_mention(target)}" if target else ""
    await message.answer(
        f"{user_mention(creator)} {color_text} rangda o'ynamoqchi.{target_text}\nO'yin turini tanlang:",
        reply_markup=challenge_type_keyboard(challenge_id),
    )


@router.callback_query(F.data.startswith("bg:type:"))
async def choose_game_type(callback: CallbackQuery):
    _, _, challenge_id, game_type = callback.data.split(":")
    challenge = PENDING_CHALLENGES.get(challenge_id)
    if not challenge:
        await callback.answer("Challenge topilmadi yoki eskirgan.", show_alert=True)
        return
    if callback.from_user.id != challenge["creator_tg_id"]:
        await callback.answer("O'yin turini faqat yaratuvchi tanlaydi.", show_alert=True)
        return

    challenge["game_type"] = game_type
    title = "Shaxmat" if game_type == "chess" else "Shashka"
    await callback.message.edit_text(
        f"{title} tanlandi.\nVaqt limitini tanlang:",
        reply_markup=challenge_time_keyboard(challenge_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bg:time:"))
async def choose_time(callback: CallbackQuery):
    _, _, challenge_id, minutes_text = callback.data.split(":")
    challenge = PENDING_CHALLENGES.get(challenge_id)
    if not challenge:
        await callback.answer("Challenge topilmadi yoki eskirgan.", show_alert=True)
        return
    if callback.from_user.id != challenge["creator_tg_id"]:
        await callback.answer("Vaqtni faqat yaratuvchi tanlaydi.", show_alert=True)
        return

    minutes = int(minutes_text)
    challenge["time_control"] = minutes
    game_name = "shaxmat" if challenge["game_type"] == "chess" else "shashka"
    color_name = "oq" if challenge["creator_color"] == "white" else "qora"
    target_text = f"Raqib: {challenge['target_name']}\n" if challenge.get("target_name") else ""
    await callback.message.edit_text(
        f"{challenge['creator_name']} {game_name} o'yiniga chaqiryapti.\n"
        f"Yaratuvchi: {color_name}\n"
        f"{target_text}"
        f"Vaqt: {minutes}+{increment_for(minutes)}\n\n"
        "Kim o'ynaydi?",
        reply_markup=accept_keyboard(challenge_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bg:cancel_challenge:"))
async def cancel_challenge(callback: CallbackQuery):
    challenge_id = callback.data.split(":")[2]
    challenge = PENDING_CHALLENGES.get(challenge_id)
    if not challenge:
        await callback.answer("Challenge allaqachon yopilgan.")
        return
    if callback.from_user.id != challenge["creator_tg_id"]:
        await callback.answer("Challenge'ni faqat yaratuvchi bekor qiladi.", show_alert=True)
        return
    PENDING_CHALLENGES.pop(challenge_id, None)
    await callback.message.edit_text("Challenge bekor qilindi.")
    await callback.answer()


@router.callback_query(F.data.startswith("bg:accept:"))
async def accept_challenge(callback: CallbackQuery):
    challenge_id = callback.data.split(":")[2]
    challenge = PENDING_CHALLENGES.get(challenge_id)
    if not challenge:
        await callback.answer("Challenge topilmadi yoki eskirgan.", show_alert=True)
        return
    if callback.from_user.id == challenge["creator_tg_id"]:
        await callback.answer("O'zingizga qarshi o'ynay olmaysiz.", show_alert=True)
        return
    if challenge.get("target_tg_id") and callback.from_user.id != challenge["target_tg_id"]:
        await callback.answer("Bu challenge faqat reply qilingan foydalanuvchi uchun.", show_alert=True)
        return
    if callback.from_user.is_bot:
        await callback.answer("Botlar o'yinga kira olmaydi.", show_alert=True)
        return

    creator = await User.get(id=challenge["creator_id"])
    opponent = await get_or_create_user(callback.from_user)
    if await active_games_count(creator) >= 2:
        await callback.answer("Yaratuvchida active o'yinlar soni 2 taga yetgan.", show_alert=True)
        return
    if await active_games_count(opponent) >= 2:
        await callback.answer("Sizda active o'yinlar soni 2 taga yetgan.", show_alert=True)
        return

    creator_color = challenge["creator_color"]
    white_player = creator if creator_color == "white" else opponent
    black_player = opponent if creator_color == "white" else creator
    minutes = challenge["time_control"]
    now = utc_now()
    common = {
        "white_player": white_player,
        "black_player": black_player,
        "chat_id": challenge["chat_id"],
        "chat_type": challenge["chat_type"],
        "message_id": callback.message.message_id,
        "time_control": minutes,
        "white_time_left": initial_seconds(minutes),
        "black_time_left": initial_seconds(minutes),
        "increment_seconds": increment_for(minutes),
        "last_move_at": now,
        "started_at": now,
    }

    if challenge["game_type"] == "chess":
        game = await ChessGame.create(fen=chess.STARTING_FEN, **common)
        markup = chess_keyboard(game)
        text = game_text("chess", game)
    else:
        game = await CheckersGame.create(board_state=checkers.initial_board(), **common)
        markup = checkers_keyboard(game)
        text = game_text("checkers", game)

    PENDING_CHALLENGES.pop(challenge_id, None)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer("O'yin boshlandi!")
