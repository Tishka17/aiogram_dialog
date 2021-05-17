from typing import Any

from aiogram.dispatcher.middlewares import BaseMiddleware

from .manager import ManagerImpl
from .protocols import DialogManager, DialogRegistryProto

MANAGER_KEY = "dialog_manager"


class ManagerMiddleware(BaseMiddleware):
    def __init__(self, registry: DialogRegistryProto):
        super().__init__()
        self.registry = registry

    async def on_pre_process_message(self, event: Any, data: dict):
        data[MANAGER_KEY] = ManagerImpl(
            event=event,
            registry=self.registry,
            data=data,
        )

    on_pre_process_callback_query = on_pre_process_message
    on_pre_process_aiogd_update = on_pre_process_message

    async def on_post_process_message(self, _, result, data: dict):
        manager: DialogManager = data.pop("dialog_manager")
        await manager.close_manager()

    on_post_process_callback_query = on_post_process_message
    on_post_process_aiogd_update = on_post_process_message
