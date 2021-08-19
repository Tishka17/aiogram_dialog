import warnings
from typing import Any, Callable, Dict, Awaitable, Optional, Union

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update, TelegramObject

from .manager import ManagerImpl
from .protocols import DialogManager, DialogRegistryProto
from ..context.events import DialogUpdateEvent

MANAGER_KEY = "dialog_manager"


class ManagerMiddleware(BaseMiddleware):
    def __init__(self, registry: DialogRegistryProto):
        super().__init__()
        self.registry = registry

    async def __call__(
            self,
            handler: Callable[[Union[Update, DialogUpdateEvent], Dict[str, Any]], Awaitable[Any]],
            event: Union[Update, DialogUpdateEvent],
            data: Dict[str, Any],
    ) -> Any:

        if isinstance(event, DialogUpdateEvent):
            content = event
        else:
            content = detect_content_type(event)

        data[MANAGER_KEY] = ManagerImpl(
            event=content,
            registry=self.registry,
            data=data,
        )

        try:
            return await handler(event, data)
        finally:
            manager: DialogManager = data.pop(MANAGER_KEY)
            await manager.close_manager()


def detect_content_type(update):
    event: Optional[TelegramObject]
    if update.message:
        event = update.message
    elif update.edited_message:
        event = update.edited_message
    elif update.channel_post:
        event = update.channel_post
    elif update.edited_channel_post:
        event = update.edited_channel_post
    elif update.inline_query:
        event = update.inline_query
    elif update.chosen_inline_result:
        event = update.chosen_inline_result
    elif update.callback_query:
        event = update.callback_query
    elif update.shipping_query:
        event = update.shipping_query
    elif update.pre_checkout_query:
        event = update.pre_checkout_query
    elif update.poll:
        event = update.poll
    elif update.poll_answer:
        event = update.poll_answer
    elif update.my_chat_member:
        event = update.my_chat_member
    elif update.chat_member:
        event = update.chat_member
    else:
        warnings.warn(
            "Detected unknown update type.\n"
            "Seems like Telegram Bot API was updated and you have "
            "installed not latest version of aiogram framework",
            RuntimeWarning,
        )
        return None
    return event
