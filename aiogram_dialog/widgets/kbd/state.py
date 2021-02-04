from typing import Callable, Optional

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery

from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Text, Const
from .button import Button, OnClick
from ..when import WhenCondition


class SwitchState(Button):
    def __init__(self, text: Text, id: str,
                 state: State,
                 on_click: Optional[OnClick] = None,
                 when: WhenCondition = None):
        super().__init__(text, id, self._on_click, when)
        self.text = text
        self.user_on_click = on_click
        self.state = state

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, self, manager)
        await manager.dialog().switch_to(self.state, manager)


class Next(Button):
    def __init__(self, text: Text = Const("Next"), callback_data: str = "__next__",
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
    def __init__(self, text: Text = Const("Back"), id: str = "__back__",
                 on_click: Optional[Callable] = None,
                 when: WhenCondition = None):
        super().__init__(text, id, self._on_click, when)
        self.text = text
        self.callback_data = id
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, button, manager)
        await manager.dialog().back(manager)


class Cancel(Button):
    def __init__(self, text: Text = Const("Cancel"), id: str = "__cancel__",
                 on_click: Optional[Callable] = None,
                 when: WhenCondition = None):
        super().__init__(text, id, self._on_click, when)
        self.text = text
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, button, manager)
        await manager.done()


class Start(Button):
    def __init__(self, text: Text, id: str,
                 state: State,
                 on_click: Optional[OnClick] = None,
                 reset_stack: bool = False,
                 when: WhenCondition = None):
        super().__init__(text, id, self._on_click, when)
        self.text = text
        self.user_on_click = on_click
        self.state = state
        self.reset_stack = reset_stack

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, self, manager)
        await manager.start(self.state, reset_stack=self.reset_stack)
