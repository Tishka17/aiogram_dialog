from aiogram.types import InlineKeyboardMarkup

from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal.widgets import (
    MarkupFactory, MarkupVariant, RawKeyboard,
)


class InlineKeyboardFactory(MarkupFactory):
    async def render_markup(
            self, data: dict, manager: DialogManager, keyboard: RawKeyboard,
    ) -> MarkupVariant:
        # TODO validate buttons
        return InlineKeyboardMarkup(
            inline_keyboard=keyboard,
        )
