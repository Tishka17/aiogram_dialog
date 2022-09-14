from typing import Awaitable, Callable, Sequence, Union

from aiogram.filters.content_types import ContentTypesFilter
from aiogram.types import ContentType, Message

from aiogram_dialog.api.internal import InputWidget
from aiogram_dialog.api.protocols import (
    DialogManager, DialogProtocol,
)
from aiogram_dialog.widgets.common import Actionable
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor,
    WidgetEventProcessor,
)

MessageHandlerFunc = Callable[
    [Message, DialogProtocol, DialogManager],
    Awaitable,
]


class BaseInput(Actionable, InputWidget):
    async def process_message(
            self, message: Message, dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        raise NotImplementedError


class MessageInput(BaseInput):
    def __init__(
            self,
            func: Union[MessageHandlerFunc, WidgetEventProcessor, None],
            content_types: Union[Sequence[str], str] = ContentType.ANY,
    ):
        super().__init__()
        self.func = ensure_event_processor(func)
        self.filter = ContentTypesFilter(content_types=content_types)

    async def process_message(
            self,
            message: Message,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        if not await self.filter(message):
            return False
        await self.func.process_event(message, self, manager)
        return True
