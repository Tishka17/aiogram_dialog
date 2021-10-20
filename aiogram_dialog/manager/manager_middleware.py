from typing import Any, Callable, Dict, Awaitable, Union, cast

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update

from .manager import ManagerImpl
from .protocols import DialogManager, DialogRegistryProto
from ..context.events import DialogUpdateEvent, DIALOG_EVENT_NAME, ChatEvent

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

        if event.event_type in ['message', 'callback_query', 'my_chat_member', DIALOG_EVENT_NAME]:
            content: ChatEvent = cast(ChatEvent, event.event)

            data[MANAGER_KEY] = ManagerImpl(
                event=content,
                registry=self.registry,
                data=data,
            )

        try:
            return await handler(event, data)
        finally:
            manager: DialogManager = data.pop(MANAGER_KEY, None)
            if manager:
                await manager.close_manager()
