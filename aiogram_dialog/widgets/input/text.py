from typing import Callable, TypeVar, Generic, Optional, Awaitable

from aiogram.types import Message, ContentType

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.action import Actionable


class BaseInput(Actionable):
    async def process_message(self, m: Message, dialog: Dialog, manager: DialogManager):
        raise NotImplementedError


T = TypeVar("T")
TypeFactory = Callable[[str], T]
OnSuccess = Callable[[T, "TextInput", DialogManager], Awaitable]
OnError = Callable[[str, "TextInput", DialogManager], Awaitable]


class TextInput(BaseInput, Generic[T]):
    def __init__(self, id: str, type_factory: TypeFactory[T] = str, on_success: Optional[OnSuccess[T]] = None,
                 on_error: Optional[OnError] = None):
        super().__init__(id)
        self.type_factory = type_factory
        self.on_success = on_success
        self.on_error = on_error

    async def process_message(self, message: Message, dialog: Dialog, manager: DialogManager):
        if message.content_type != ContentType.TEXT:
            return False
        try:
            value = self.type_factory(message.text)
            if self.on_success:
                self.on_success(value, self, manager)
            manager.context.set_data(self.widget_id, message.text, internal=True)  # store original text
        except ValueError:
            if self.on_error:
                await self.on_error(message.text, self, manager)

    def get_value(self, manager: DialogManager):
        return self.type_factory(manager.context.data(self.widget_id, internal=True))
