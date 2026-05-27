from asyncio import sleep
from typing import Any, Awaitable, Callable

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter


async def retry_telegram(call: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
    for attempt in range(3):
        try:
            return await call(*args, **kwargs)
        except TelegramRetryAfter as exc:
            await sleep(float(exc.retry_after) + 0.5)
        except TelegramBadRequest as exc:
            if "message is not modified" in str(exc).lower():
                return None
            raise
    return await call(*args, **kwargs)


async def answer_message(message, *args, **kwargs) -> Any:
    return await retry_telegram(message.answer, *args, **kwargs)


async def answer_callback(callback, *args, **kwargs) -> Any:
    return await retry_telegram(callback.answer, *args, **kwargs)


async def edit_message_text(message, *args, **kwargs) -> Any:
    return await retry_telegram(message.edit_text, *args, **kwargs)


async def edit_message_reply_markup(message, *args, **kwargs) -> Any:
    return await retry_telegram(message.edit_reply_markup, *args, **kwargs)
