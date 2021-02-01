from typing import Callable, Optional, Union, Dict

from aiogram.types import CallbackQuery

from dialog.manager.manager import DialogManager
from dialog.widgets.text import Text, Case
from .button import Button
from ...dialog import Dialog


class Checkbox(Button):
    def __init__(self, checked_text: Text, unchecked_text: Text,
                 callback_data: str,
                 id: str,
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        text = Case({True: checked_text, False: unchecked_text}, selector=self._is_text_checked)
        super().__init__(text, callback_data, self._on_click, when)
        self.widget_id = id
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        manager.context.set_data(self.widget_id, not self.is_checked(manager), internal=True)

    def _is_text_checked(self, data: Dict, case: Case, manager: DialogManager) -> bool:
        return self.is_checked(manager)

    def is_checked(self, manager: DialogManager) -> bool:
        return manager.context.data(self.widget_id, False, internal=True)
