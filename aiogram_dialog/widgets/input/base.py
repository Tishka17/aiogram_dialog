from typing import Callable, Awaitable, List, Union

from aiogram.dispatcher.filters import ContentTypeFilter
from aiogram.types import Message

from aiogram_dialog.manager.protocols import (
    DialogManager, ManagedDialogAdapterProto, ManagedDialogProto
)
from aiogram_dialog.widgets.action import Actionable
from aiogram_dialog.widgets.widget_event import (
    WidgetEventProcessor, ensure_event_processor,
)

MessageHandlerFunc = Callable[
    [Message, ManagedDialogAdapterProto, DialogManager],
    Awaitable,
]


class BaseInput(Actionable):
    async def process_message(self, m: Message, dialog: ManagedDialogProto, manager: DialogManager) -> bool:
        raise NotImplementedError


class MessageInput(BaseInput):
    def __init__(self, func: Union[MessageHandlerFunc, WidgetEventProcessor, None],
                 content_types: List[str] = ContentTypeFilter.default):
        super().__init__()
        self.func = ensure_event_processor(func)
        self.filter = ContentTypeFilter(content_types)

    async def process_message(self, message: Message, dialog: ManagedDialogProto, manager: DialogManager) -> bool:
        if not await self.filter.check(message):
            return False
        await self.func.process_event(message, manager.dialog(), manager)
        return True
