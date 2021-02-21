from typing import Callable, Awaitable

from aiogram.types import Message

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.action import Actionable

MessageHandlerFunc = Callable[[Message, Dialog, DialogManager], Awaitable]


class BaseInput(Actionable):
    async def process_message(self, m: Message, dialog: Dialog, manager: DialogManager) -> bool:
        return False


class MessageInput(BaseInput):
    def __init__(self, func: MessageHandlerFunc):
        super().__init__()
        self.func = func

    async def process_message(self, m: Message, dialog: Dialog, manager: DialogManager) -> bool:
        await self.func(m, dialog, manager)
        return True
