from typing import Callable, TypeVar, Generic, Awaitable, Union, Optional

from aiogram.types import Message, ContentType

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.protocols import DialogManager
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor, ensure_event_processor
from .base import BaseInput
from ..managed import ManagedWidgetAdapter
from ...deprecation_utils import manager_deprecated

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

    def get_value(self, manager: DialogManager) -> T:
        return self.type_factory(manager.current_context().widget_data[self.widget_id])

    def managed(self, manager: DialogManager):
        return ManagedTextInputAdapter(self, manager)


class ManagedTextInputAdapter(ManagedWidgetAdapter[TextInput[T]], Generic[T]):

    def get_value(self, manager: Optional[DialogManager] = None) -> T:
        manager_deprecated(manager)
        return self.widget.get_value(self.manager)
