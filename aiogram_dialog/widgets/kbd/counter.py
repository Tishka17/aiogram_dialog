from typing import List, Dict, Optional, Callable, Awaitable, Union

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.context.events import ChatEvent
from aiogram_dialog.manager.protocols import DialogManager, ManagedDialogProto
from aiogram_dialog.widgets.kbd.base import Keyboard
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format, Text
from aiogram_dialog.widgets.when import WhenCondition
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor, \
    ensure_event_processor

OnClick = Callable[
    [ChatEvent, "ManagedCounterAdapter", DialogManager],
    Awaitable,
]
OnValueChanged = Callable[
    [ChatEvent, "ManagedCounterAdapter", DialogManager],
    Awaitable,
]


class Counter(Keyboard):
    def __init__(
            self, id: str,
            plus: Optional[Text] = Const("+"),
            minus: Optional[Text] = Const("-"),
            text: Optional[Text] = Format("{value:g}"),
            min_value: float = 0, max_value: float = 999999,
            increment: float = 1, default: float = 0,
            cycle: bool = False,
            on_click: Union[OnClick, WidgetEventProcessor, None] = None,
            on_value_changed: Union[
                OnValueChanged, WidgetEventProcessor, None
            ] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.plus = plus
        self.minus = minus
        self.min = min_value
        self.max = max_value
        self.increment = increment
        self.default = default
        self.text = text
        self.cycle = cycle
        self.on_click = ensure_event_processor(on_click)
        self.on_value_changed = ensure_event_processor(on_value_changed)

    def get_value(self, manager: DialogManager) -> float:
        return manager.current_context().widget_data.get(
            self.widget_id, self.default
        )

    async def set_value(self, manager: DialogManager, value: float) -> None:
        if self.min <= value <= self.max:
            manager.current_context().widget_data[self.widget_id] = value
            await self.on_value_changed.process_event(
                manager.event, self.managed(manager), manager,
            )

    async def _render_keyboard(
            self, data: Dict, manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        row = []
        if self.minus:
            minus = await self.minus.render_text(data, manager)
            row.append(InlineKeyboardButton(
                text=minus, callback_data=self._item_callback_data("-"),
            ))
        if self.text:
            text = await self.text.render_text(
                {"value": self.get_value(manager), "data": data},
                manager,
            )
            row.append(InlineKeyboardButton(
                text=text, callback_data=self._item_callback_data(""),
            ))
        if self.plus:
            plus = await self.plus.render_text(data, manager)
            row.append(InlineKeyboardButton(
                text=plus, callback_data=self._item_callback_data("+"),
            ))
        return [row]

    async def _process_item_callback(
            self, c: CallbackQuery, data: str, dialog: ManagedDialogProto,
            manager: DialogManager,
    ) -> bool:
        await self.on_click.process_event(c, self.managed(manager), manager)

        value = self.get_value(manager)
        if data == "+":
            value += self.increment
            if value > self.max and self.cycle:
                value = self.min
            await self.set_value(manager, value)
        elif data == "-":
            value -= self.increment
            if value < self.min and self.cycle:
                value = self.max
            await self.set_value(manager, value)
        return True

    def get_page(self, manager: DialogManager) -> int:
        return manager.current_context().widget_data.get(self.widget_id, 0)

    def managed(self, manager: DialogManager):
        return ManagedCounterAdapter(self, manager)


class ManagedCounterAdapter(ManagedWidgetAdapter[Counter]):

    def get_value(self) -> float:
        return self.widget.get_value(self.manager)

    async def set_value(self, value: float) -> None:
        await self.widget.set_value(self.manager, value)
