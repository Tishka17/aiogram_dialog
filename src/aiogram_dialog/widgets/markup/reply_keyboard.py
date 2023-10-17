from typing import Optional

from aiogram.types import ReplyKeyboardMarkup

from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal.widgets import (
    MarkupFactory, RawKeyboard, MarkupVariant,
)
from aiogram_dialog.utils import transform_to_reply_keyboard
from aiogram_dialog.widgets.text import Text


class ReplyKeyboardFactory(MarkupFactory):
    def __init__(
            self,
            resize_keyboard: Optional[bool] = None,
            one_time_keyboard: Optional[bool] = None,
            input_field_placeholder: Optional[Text] = None,
            selective: Optional[bool] = None,
    ):
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.input_field_placeholder = input_field_placeholder
        self.selective = selective

    async def render_markup(
            self, data: dict, manager: DialogManager, keyboard: RawKeyboard,
    ) -> MarkupVariant:
        if self.input_field_placeholder:
            placeholder = await self.input_field_placeholder.render_text(
                data, manager,
            )
        else:
            placeholder = None
        return ReplyKeyboardMarkup(
            keyboard=transform_to_reply_keyboard(keyboard),
            resize_keyboard=self.resize_keyboard,
            one_time_keyboard=self.one_time_keyboard,
            input_field_placeholder=placeholder,
            selective=self.selective,
        )
