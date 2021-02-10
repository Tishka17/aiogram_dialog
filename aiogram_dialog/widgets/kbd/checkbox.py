from typing import Callable, Optional, Union, Dict, Awaitable

from aiogram.types import CallbackQuery

from aiogram_dialog.manager.intent import ChatEvent
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Text, Case
from .button import Button

OnStateChanged = Callable[[ChatEvent, "Checkbox", DialogManager], Awaitable]


class Checkbox(Button):
    def __init__(self, checked_text: Text, unchecked_text: Text,
                 id: str,
                 on_state_changed: Optional[OnStateChanged] = None,
                 default: bool = False,
                 when: Union[str, Callable] = None):
        text = Case({True: checked_text, False: unchecked_text}, selector=self._is_text_checked)
        super().__init__(text, id, self._on_click, when)
        self.default = default
        self.on_state_changed = on_state_changed

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        await self.set_checked(c, not self.is_checked(manager), manager)

    def _is_text_checked(self, data: Dict, case: Case, manager: DialogManager) -> bool:
        return self.is_checked(manager)

    def is_checked(self, manager: DialogManager) -> bool:
        return manager.context.data(self.widget_id, self.default, internal=True)

    async def set_checked(self, event: ChatEvent, checked: bool, manager: DialogManager):
        manager.context.set_data(self.widget_id, checked, internal=True)
        if self.on_state_changed:
            await self.on_state_changed(event, self, manager)
