from contextvars import copy_context
from typing import Any

from aiogram import Bot

from aiogram_dialog.api.entities import DialogUpdate
from aiogram_dialog.manager.updater import Updater


class SimpleUpdater(Updater):
    async def notify(self, bot: Bot, update: DialogUpdate) -> Any:
        context = copy_context()
        return await context.run(self._process_update, bot, update)
