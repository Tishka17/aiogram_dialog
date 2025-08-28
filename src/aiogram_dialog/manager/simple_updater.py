from contextvars import copy_context

from aiogram import Bot

from aiogram_dialog.api.entities import DialogUpdate
from aiogram_dialog.manager.updater import Updater


class SimpleUpdater(Updater):
    async def notify(self, bot: Bot, update: DialogUpdate) -> None:
        context = copy_context()
        await context.run(self._process_update, bot, update)
