from secrets import token_hex

import chess
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.board import checkers_keyboard, chess_keyboard, game_text
from keyboards.challenge import accept_keyboard, challenge_time_keyboard, challenge_type_keyboard
from models.board_game import CheckersGame, ChessGame
from models.user import User
from config import ShaxmatEmojies
from services import checkers
from services.telegram_safe import answer_callback, answer_message, edit_bot_message_text, edit_message_text
from services.time_control import increment_for, initial_seconds, utc_now
from services.users import active_games_count, get_or_create_user, user_mention

router = Router()
PENDING_CHALLENGES: dict[str, dict] = {}


def create_pending_challenge(creator: User, creator_color: str, chat_id: int, chat_type: str) -> str:
    challenge_id = token_hex(3)
    PENDING_CHALLENGES[challenge_id] = {
        "creator_id": creator.id,
        "creator_tg_id": creator.user_id,
        "creator_name": user_mention(creator),
        "creator_color": creator_color,
        "target_tg_id": None,
        "target_name": None,
        "chat_id": chat_id,
        "chat_type": chat_type,
    }
    return challenge_id


def inline_challenge_text(creator: User, creator_color: str) -> str:
    color_text = "oq" if creator_color == "white" else "qora"
    return f"{user_mention(creator)} {color_text} rangda o'ynamoqchi.\nO'yin turini tanlang:"


async def edit_challenge_message(callback: CallbackQuery, text: str, reply_markup=None):
    if callback.inline_message_id:
        await edit_bot_message_text(
            callback.bot,
            inline_message_id=callback.inline_message_id,
            text=text,
            reply_markup=reply_markup,
        )
        return
    await edit_message_text(callback.message, text, reply_markup=reply_markup)


@router.message(Command("start"))
async def start_handler(message: Message):
    await answer_message(
        message,
        "Univers Chess.\n\n"
        "O'yinni inline mode orqali boshlang: istalgan chatda bot username'ini yozing va "
        "oq yoki qora rangni tanlang. Keyin xabarning o'zida shaxmat yoki shashka tanlanadi."
    )


@router.message(Command("chesswhite", "chessblack", "chessbalck"))
async def create_challenge(message: Message):
    await answer_message(
        message,
        "Endi o'yin inline mode orqali boshlanadi. Chat inputiga bot username'ini yozing, "
        "keyin oq yoki qora bo'lib boshlash variantini tanlang."
    )
    return


@router.message(Command("emojitest"))
async def emoji_test(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=".",
        callback_data="bg:noop",
        icon_custom_emoji_id=str(ShaxmatEmojies.WHITE_QIROL),
        style="success",
    )
    keyboard.button(
        text=".",
        callback_data="bg:noop",
        icon_custom_emoji_id=str(ShaxmatEmojies.BLACK_QIROL),
        style="danger",
    )
    keyboard.adjust(2)
    await answer_message(message, "Custom emoji direct-message testi:", reply_markup=keyboard.as_markup())


@router.inline_query()
async def inline_challenge(inline_query: InlineQuery):
    creator = await get_or_create_user(inline_query.from_user)
    if await active_games_count(creator) >= 2:
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    id="limit",
                    title="Active o'yinlar limiti to'lgan",
                    description="Yangi o'yin boshlash uchun oldingi active o'yinlardan birini tugating.",
                    input_message_content=InputTextMessageContent(
                        message_text="Sizda active o'yinlar soni 2 taga yetgan."
                    ),
                )
            ],
            cache_time=0,
            is_personal=True,
        )
        return

    white_challenge_id = create_pending_challenge(creator, "white", 0, "inline")
    black_challenge_id = create_pending_challenge(creator, "black", 0, "inline")
    await inline_query.answer(
        [
            InlineQueryResultArticle(
                id=white_challenge_id,
                title="Oq bo'lib boshlash",
                description="Raqib qora rangda o'ynaydi.",
                input_message_content=InputTextMessageContent(
                    message_text=inline_challenge_text(creator, "white")
                ),
                reply_markup=challenge_type_keyboard(white_challenge_id),
            ),
            InlineQueryResultArticle(
                id=black_challenge_id,
                title="Qora bo'lib boshlash",
                description="Raqib oq rangda o'ynaydi.",
                input_message_content=InputTextMessageContent(
                    message_text=inline_challenge_text(creator, "black")
                ),
                reply_markup=challenge_type_keyboard(black_challenge_id),
            ),
        ],
        cache_time=0,
        is_personal=True,
    )


@router.callback_query(F.data.startswith("bg:type:"))
async def choose_game_type(callback: CallbackQuery):
    _, _, challenge_id, game_type = callback.data.split(":")
    challenge = PENDING_CHALLENGES.get(challenge_id)
    if not challenge:
        await answer_callback(callback, "Challenge topilmadi yoki eskirgan.", show_alert=True)
        return
    if callback.from_user.id != challenge["creator_tg_id"]:
        await answer_callback(callback, "O'yin turini faqat yaratuvchi tanlaydi.", show_alert=True)
        return

    if callback.inline_message_id:
        challenge["inline_message_id"] = callback.inline_message_id
    challenge["game_type"] = game_type
    title = "Shaxmat" if game_type == "chess" else "Shashka"
    await edit_challenge_message(
        callback,
        f"{title} tanlandi.\nVaqt limitini tanlang:",
        reply_markup=challenge_time_keyboard(challenge_id),
    )
    await answer_callback(callback)


@router.callback_query(F.data.startswith("bg:time:"))
async def choose_time(callback: CallbackQuery):
    _, _, challenge_id, minutes_text = callback.data.split(":")
    challenge = PENDING_CHALLENGES.get(challenge_id)
    if not challenge:
        await answer_callback(callback, "Challenge topilmadi yoki eskirgan.", show_alert=True)
        return
    if callback.from_user.id != challenge["creator_tg_id"]:
        await answer_callback(callback, "Vaqtni faqat yaratuvchi tanlaydi.", show_alert=True)
        return

    if callback.inline_message_id:
        challenge["inline_message_id"] = callback.inline_message_id
    minutes = int(minutes_text)
    challenge["time_control"] = minutes
    game_name = "shaxmat" if challenge["game_type"] == "chess" else "shashka"
    color_name = "oq" if challenge["creator_color"] == "white" else "qora"
    target_text = f"Raqib: {challenge['target_name']}\n" if challenge.get("target_name") else ""
    await edit_challenge_message(
        callback,
        f"{challenge['creator_name']} {game_name} o'yiniga chaqiryapti.\n"
        f"Yaratuvchi: {color_name}\n"
        f"{target_text}"
        f"Vaqt: {minutes}+{increment_for(minutes)}\n\n"
        "Kim o'ynaydi?",
        reply_markup=accept_keyboard(challenge_id),
    )
    await answer_callback(callback)


@router.callback_query(F.data.startswith("bg:cancel_challenge:"))
async def cancel_challenge(callback: CallbackQuery):
    challenge_id = callback.data.split(":")[2]
    challenge = PENDING_CHALLENGES.get(challenge_id)
    if not challenge:
        await answer_callback(callback, "Challenge allaqachon yopilgan.")
        return
    if callback.from_user.id != challenge["creator_tg_id"]:
        await answer_callback(callback, "Challenge'ni faqat yaratuvchi bekor qiladi.", show_alert=True)
        return
    PENDING_CHALLENGES.pop(challenge_id, None)
    await edit_challenge_message(callback, "Challenge bekor qilindi.")
    await answer_callback(callback)


@router.callback_query(F.data.startswith("bg:accept:"))
async def accept_challenge(callback: CallbackQuery):
    challenge_id = callback.data.split(":")[2]
    challenge = PENDING_CHALLENGES.get(challenge_id)
    if not challenge:
        await answer_callback(callback, "Challenge topilmadi yoki eskirgan.", show_alert=True)
        return
    if callback.from_user.id == challenge["creator_tg_id"]:
        await answer_callback(callback, "O'zingizga qarshi o'ynay olmaysiz.", show_alert=True)
        return
    if challenge.get("target_tg_id") and callback.from_user.id != challenge["target_tg_id"]:
        await answer_callback(callback, "Bu challenge faqat reply qilingan foydalanuvchi uchun.", show_alert=True)
        return
    if callback.from_user.is_bot:
        await answer_callback(callback, "Botlar o'yinga kira olmaydi.", show_alert=True)
        return

    creator = await User.get(id=challenge["creator_id"])
    opponent = await get_or_create_user(callback.from_user)
    if await active_games_count(creator) >= 2:
        await answer_callback(callback, "Yaratuvchida active o'yinlar soni 2 taga yetgan.", show_alert=True)
        return
    if await active_games_count(opponent) >= 2:
        await answer_callback(callback, "Sizda active o'yinlar soni 2 taga yetgan.", show_alert=True)
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
        "message_id": None if callback.inline_message_id else callback.message.message_id,
        "inline_message_id": callback.inline_message_id or challenge.get("inline_message_id"),
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
    await edit_challenge_message(callback, text, reply_markup=markup)
    await answer_callback(callback, "O'yin boshlandi!")
