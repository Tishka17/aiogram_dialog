from typing import Any, Callable, Dict, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update

from .manager import ManagerImpl
from .protocols import DialogManager, DialogRegistryProto

MANAGER_KEY = "dialog_manager"


class ManagerMiddleware(BaseMiddleware):
    def __init__(self, registry: DialogRegistryProto):
        super().__init__()
        self.registry = registry

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        data[MANAGER_KEY] = ManagerImpl(
            event=event,
            registry=self.registry,
            data=data,
        )

        result = await handler(event, data)

        manager: DialogManager = data.pop("dialog_manager")
        await manager.close_manager()

        return result
