from typing import Any

from aiogram.types import CopyTextButton, InlineKeyboardButton

from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Keyboard
from aiogram_dialog.widgets.text import Text


class CopyText(Keyboard):
    def __init__(
        self,
        text: Text,
        copy_text: Text,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(when=when)
        self._text = text
        self._copy_text = copy_text

    async def _render_keyboard(
        self,
        data: dict[str, Any],
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                InlineKeyboardButton(
                    text=await self._text.render_text(data, manager),
                    copy_text=CopyTextButton(
                        text=await self._copy_text.render_text(data, manager),
                    ),
                ),
            ],
        ]
