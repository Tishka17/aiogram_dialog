from typing import Callable, Awaitable, List

from aiogram.dispatcher.filters import ContentTypeFilter
from aiogram.types import Message, ContentTypes

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.action import Actionable

MessageHandlerFunc = Callable[[Message, Dialog, DialogManager], Awaitable]


class BaseInput(Actionable):
    async def process_message(self, m: Message, dialog: Dialog, manager: DialogManager) -> bool:
        return False


class MessageInput(BaseInput):
    def __init__(self, func: MessageHandlerFunc, content_types: List[str] = ContentTypes.TEXT):
        super().__init__()
        self.func = func
        self.filter = ContentTypeFilter(content_types)

    async def process_message(self, message: Message, dialog: Dialog, manager: DialogManager) -> bool:
        if not await self.filter.check(message):
            return False
        await self.func(message, dialog, manager)
        return True
