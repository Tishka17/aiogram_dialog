from typing import Callable, Optional, Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery

from aiogram_dialog.context.events import ChatEvent, StartMode
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Text, Const
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor
from .button import Button, OnClick
from ..when import WhenCondition


class EventProcessorButton(Button, WidgetEventProcessor):
    async def process_event(self, event: ChatEvent, source: Any, manager: DialogManager,
                            *args, **kwargs):
        await self._on_click(event, self, manager)

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        raise NotImplementedError


class SwitchTo(EventProcessorButton):

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


class Next(EventProcessorButton):
    def __init__(self, text: Text = Const("Next"), callback_data: str = "__next__",
                 on_click: Optional[Callable] = None,
                 when: WhenCondition = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, self, manager)
        await manager.dialog().next(manager)


class Back(EventProcessorButton):
    def __init__(self, text: Text = Const("Back"), id: str = "__back__",
                 on_click: Optional[Callable] = None,
                 when: WhenCondition = None):
        super().__init__(text, id, self._on_click, when)
        self.text = text
        self.callback_data = id
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, self, manager)
        await manager.dialog().back(manager)


class Cancel(EventProcessorButton):
    def __init__(self, text: Text = Const("Cancel"), id: str = "__cancel__",
                 on_click: Optional[Callable] = None,
                 when: WhenCondition = None):
        super().__init__(text, id, self._on_click, when)
        self.text = text
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, self, manager)
        await manager.done()


class Start(EventProcessorButton):
    def __init__(self, text: Text, id: str,
                 state: State,
                 on_click: Optional[OnClick] = None,
                 mode: StartMode = StartMode.NORMAL,
                 when: WhenCondition = None):
        super().__init__(text, id, self._on_click, when)
        self.text = text
        self.user_on_click = on_click
        self.state = state
        self.mode = mode

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, self, manager)
        await manager.start(self.state, mode=self.mode)
