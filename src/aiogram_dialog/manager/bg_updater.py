import asyncio
from contextvars import copy_context

from aiogram import Bot

from aiogram_dialog.api.entities import DialogUpdate
from aiogram_dialog.manager.updater import Updater


class BgUpdater(Updater):
    async def notify(self, bot: Bot, update: DialogUpdate) -> None:
        def callback():
            asyncio.create_task(  # noqa: RUF006
                self._process_update(bot, update),
            )

        asyncio.get_running_loop().call_soon(callback, context=copy_context())
