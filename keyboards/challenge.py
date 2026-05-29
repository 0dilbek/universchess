from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import TIME_OPTIONS


def challenge_color_keyboard(challenge_id: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⚪ Oq", callback_data=f"bg:color:{challenge_id}:white")
    keyboard.button(text="⚫ Qora", callback_data=f"bg:color:{challenge_id}:black")
    keyboard.adjust(2)
    return keyboard.as_markup()


def challenge_type_keyboard(challenge_id: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="♟ Shaxmat", callback_data=f"bg:type:{challenge_id}:chess")
    keyboard.button(text="⚫ Shashka", callback_data=f"bg:type:{challenge_id}:checkers")
    keyboard.adjust(2)
    return keyboard.as_markup()


def challenge_time_keyboard(challenge_id: str):
    keyboard = InlineKeyboardBuilder()
    for minutes in TIME_OPTIONS:
        keyboard.button(text=f"⏱ {minutes}", callback_data=f"bg:time:{challenge_id}:{minutes}")
    keyboard.adjust(4)
    return keyboard.as_markup()


def accept_keyboard(challenge_id: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Qabul qilish", callback_data=f"bg:accept:{challenge_id}")
    keyboard.button(text="❌ Bekor qilish", callback_data=f"bg:cancel_challenge:{challenge_id}")
    keyboard.adjust(2)
    return keyboard.as_markup()
