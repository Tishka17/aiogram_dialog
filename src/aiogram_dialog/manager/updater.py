from abc import ABC, abstractmethod
from typing import Any

from aiogram import Bot, Dispatcher, Router

from aiogram_dialog.api.entities import DialogUpdate


class Updater(ABC):
    def __init__(self, dp: Router):
        while dp.parent_router:
            dp = dp.parent_router
        if not isinstance(dp, Dispatcher):
            raise TypeError("Root router must be Dispatcher.")
        self.dp = dp

    @abstractmethod
    async def notify(self, bot: Bot, update: DialogUpdate) -> Any:
        pass

    async def _process_update(self, bot: Bot, update: DialogUpdate) -> Any:
        event = update.event
        return await self.dp.propagate_event(
            update_type="update",
            event=update,
            bot=bot,
            event_from_user=event.from_user,
            event_chat=event.chat,
            event_thread_id=event.thread_id,
            **self.dp.workflow_data,
        )
