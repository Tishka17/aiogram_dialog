from typing import Any

from aiogram.dispatcher.middlewares import BaseMiddleware

from .protocols import (
    DialogManager, DialogRegistryProto, DialogManagerFactory,
)

MANAGER_KEY = "dialog_manager"


class ManagerMiddleware(BaseMiddleware):
    def __init__(
            self,
            registry: DialogRegistryProto,
            dialog_manager_factory: DialogManagerFactory,
    ):
        super().__init__()
        self.registry = registry
        self.dialog_manager_factory = dialog_manager_factory

    async def on_pre_process_message(self, event: Any, data: dict):
        data[MANAGER_KEY] = self.dialog_manager_factory(
            event=event,
            registry=self.registry,
            data=data,
        )

    on_pre_process_callback_query = on_pre_process_message
    on_pre_process_aiogd_update = on_pre_process_message
    on_pre_process_my_chat_member = on_pre_process_message

    async def on_post_process_message(self, _, result, data: dict):
        manager: DialogManager = data.pop(MANAGER_KEY)
        await manager.close_manager()

    on_post_process_callback_query = on_post_process_message
    on_post_process_aiogd_update = on_post_process_message
    on_post_process_my_chat_member = on_post_process_message

    async def on_pre_process_error(self, update: Any, error: Exception,
                                   data: dict) -> None:
        event = (
                update.message or
                update.my_chat_member or
                update.callback_query
        )
        await self.on_pre_process_message(event, data)

    async def on_post_process_error(self, event: Any, error: Exception,
                                    result: list, data: dict) -> None:
        await self.on_post_process_message(event, result, data)
