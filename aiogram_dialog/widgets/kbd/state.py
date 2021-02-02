from typing import Callable, Optional

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery

from dialog.manager.manager import DialogManager
from dialog.widgets.text import Text, Const
from .button import Button, OnClick
from ..when import WhenCondition


class SwitchState(Button):
    def __init__(self, text: Text, callback_data: str,
                 state: State,
                 on_click: Optional[OnClick] = None,
                 when: WhenCondition = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click
        self.state = state.state

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, self, manager)
        await manager.dialog().switch_to(self.state, manager)


class Next(Button):
    def __init__(self, text: Text = Const("Next"), callback_data: str = "next",
                 on_click: Optional[Callable] = None,
                 when: WhenCondition = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, button, manager)
        await manager.dialog().next(manager)


class Back(Button):
    def __init__(self, text: Text = Const("Back"), callback_data: str = "back",
                 on_click: Optional[Callable] = None,
                 when: WhenCondition = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, button, manager)
        await manager.dialog().back(manager)


class Cancel(Button):
    def __init__(self, text: Text = Const("Cancel"), callback_data: str = "cancel",
                 on_click: Optional[Callable] = None,
                 when: WhenCondition = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, button, manager)
        await manager.done()
