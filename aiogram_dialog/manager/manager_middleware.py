from typing import Any, Callable, Dict, Awaitable, Union, cast

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update

from .manager import ManagerImpl
from .protocols import DialogManager, DialogRegistryProto
from ..context.events import DialogUpdateEvent, ChatEvent

MANAGER_KEY = "dialog_manager"


class ManagerMiddleware(BaseMiddleware):
    def __init__(self, registry: DialogRegistryProto):
        super().__init__()
        self.registry = registry

    async def __call__(
            self,
            handler: Callable[[Union[Update, DialogUpdateEvent], Dict[str, Any]], Awaitable[Any]],
            event: ChatEvent,
            data: Dict[str, Any],
    ) -> Any:
        data[MANAGER_KEY] = ManagerImpl(
            event=event,
            registry=self.registry,
            data=data,
        )

        try:
            return await handler(event, data)
        finally:
            manager: DialogManager = data.pop(MANAGER_KEY, None)
            if manager:
                await manager.close_manager()
