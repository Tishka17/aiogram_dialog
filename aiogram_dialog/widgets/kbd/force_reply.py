from typing import Callable, Optional, Dict, Awaitable

from aiogram.types import CallbackQuery, ForceReply as ForceReplyMarkup

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Text
from .base import Keyboard
from ..when import WhenCondition

OnClick = Callable[[CallbackQuery, "Button", DialogManager], Awaitable]


class ForceReply(Keyboard):
    def __init__(self, text: Text, id: str,
                 selective: Optional[bool] = True,
                 when: WhenCondition = None):
        super().__init__(id, when)
        self.text = text
        self.selective = selective

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        return False

    async def _render_keyboard(self, data: Dict, manager: DialogManager) -> ForceReplyMarkup:

        return ForceReplyMarkup(
                input_field_placeholder=await self.text.render_text(data, manager),
                callback_data=self.widget_id,
                selective=self.selective)
