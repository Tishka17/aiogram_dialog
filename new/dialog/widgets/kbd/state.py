from typing import Callable, Optional, Union

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery

from dialog.dialog import Dialog
from dialog.manager.manager import DialogManager
from dialog.widgets.text import Text, Const
from .button import Button


class SwitchState(Button):
    def __init__(self, text: Text, callback_data: str,
                 state: State,
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click
        self.state = state.state

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        await dialog.switch_to(self.state, manager)


class Next(Button):
    def __init__(self, text: Text = Const("Next"), callback_data: str = "next",
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        await dialog.next(manager)


class Back(Button):
    def __init__(self, text: Text = Const("Back"), callback_data: str = "back",
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        await dialog.back(manager)


class Cancel(Button):
    def __init__(self, text: Text = Const("Cancel"), callback_data: str = "cancel",
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        await manager.done()
