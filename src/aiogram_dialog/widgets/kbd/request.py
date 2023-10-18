from typing import Awaitable, Callable, Dict, List, Optional, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton, KeyboardButton

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.text import Text

from .base import Keyboard

OnClick = Callable[[CallbackQuery, "Button", DialogManager], Awaitable]


class RequestContact(Keyboard):
    def __init__(
        self,
        text: Text,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text

    async def _render_keyboard(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> List[List[KeyboardButton]]:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_contact=True,
                ),
            ],
        ]


class RequestLocation(Keyboard):
    def __init__(
        self,
        text: Text,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text

    async def _render_keyboard(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> List[List[KeyboardButton]]:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_location=True,
                ),
            ],
        ]
