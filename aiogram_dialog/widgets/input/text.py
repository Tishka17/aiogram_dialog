from typing import Callable, TypeVar, Generic, Awaitable, Union

from aiogram.types import Message, ContentType

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor, ensure_event_processor
from .base import BaseInput

T = TypeVar("T")
TypeFactory = Callable[[str], T]
OnSuccess = Callable[[Message, "TextInput", DialogManager, T], Awaitable]
OnError = Callable[[Message, "TextInput", DialogManager], Awaitable]


class TextInput(BaseInput, Generic[T]):
    def __init__(self, id: str, type_factory: TypeFactory[T] = str,
                 on_success: Union[OnSuccess[T], WidgetEventProcessor, None] = None,
                 on_error: Union[OnError, WidgetEventProcessor, None] = None):
        super().__init__(id)
        self.type_factory = type_factory
        self.on_success = ensure_event_processor(on_success)
        self.on_error = ensure_event_processor(on_error)

    async def process_message(self, message: Message, dialog: Dialog, manager: DialogManager):
        if message.content_type != ContentType.TEXT:
            return False
        try:
            value = self.type_factory(message.text)
        except ValueError:
            await self.on_error.process_event(message, self, manager)
        else:
            # store original text
            manager.current_context().widget_data[self.widget_id] = message.text
            await self.on_success.process_event(message, self, manager, value)

    def get_value(self, manager: DialogManager):
        return self.type_factory(manager.current_context().widget_data[self.widget_id])
