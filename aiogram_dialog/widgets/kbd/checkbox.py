from abc import ABC, abstractmethod
from typing import Callable, Optional, Union, Dict, Awaitable, List

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.intent import ChatEvent
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Text, Case
from .base import Keyboard

OnStateChanged = Callable[[ChatEvent, "Checkbox", DialogManager], Awaitable]


class BaseCheckbox(Keyboard, ABC):
    def __init__(self, checked_text: Text, unchecked_text: Text,
                 id: str,
                 on_state_changed: Optional[OnStateChanged] = None,
                 default: bool = False,
                 when: Union[str, Callable] = None):
        super().__init__(id, when)
        self.text = Case({True: checked_text, False: unchecked_text}, selector=self._is_text_checked)
        self.default = default
        self.on_state_changed = on_state_changed
        self._callback_data_prefix = f"{self.widget_id}:"

    async def _render_kbd(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        checked = int(self.is_checked(data, manager))
        # store current checked status in callback data
        return [[
            InlineKeyboardButton(
                text=await self.text.render_text(data, manager),
                callback_data=f"{self._callback_data_prefix}{checked}"
            )
        ]]

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        if not c.data.startswith(f"{self._callback_data_prefix}"):
            return False
        # remove prefix and cast "0" as False, "1" as True
        checked = c.data[len(self._callback_data_prefix):] != "0"
        await self.set_checked(c, not checked, manager)
        return True

    def _is_text_checked(self, data: Dict, case: Case, manager: DialogManager) -> bool:
        return self.is_checked(data, manager)

    @abstractmethod
    def is_checked(self, data: Dict, manager: DialogManager) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def set_checked(self, event: ChatEvent, checked: bool, manager: DialogManager):
        raise NotImplementedError


class Checkbox(BaseCheckbox):
    def is_checked(self, data: Dict, manager: DialogManager) -> bool:
        return manager.context.data(self.widget_id, self.default, internal=True)

    async def set_checked(self, event: ChatEvent, checked: bool, manager: DialogManager):
        manager.context.set_data(self.widget_id, checked, internal=True)
        if self.on_state_changed:
            await self.on_state_changed(event, self, manager)
