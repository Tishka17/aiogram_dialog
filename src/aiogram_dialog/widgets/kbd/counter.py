from abc import abstractmethod
from typing import Optional, Protocol, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.kbd.base import Keyboard
from aiogram_dialog.widgets.text import Const, Format, Text
from aiogram_dialog.widgets.widget_event import (
    WidgetEventProcessor,
    ensure_event_processor,
)


class OnCounterEvent(Protocol):
    @abstractmethod
    async def __call__(
            self,
            event: ChatEvent,
            counter: "ManagedCounter",  # noqa: F841, RUF100
            dialog_manager: DialogManager,
    ):
        raise NotImplementedError


OnCounterEventVariant = Union[OnCounterEvent, WidgetEventProcessor, None]

PLUS_TEXT = Const("+")
MINUS_TEXT = Const("-")
DEFAULT_COUNTER_TEXT = Format("{value:g}")


class Counter(Keyboard):
    """
    Counter widget.

    Used to represent number with increment/decrement buttons
    To remove any button set its text to `None`
    """

    def __init__(
            self,
            id: str,
            plus: Optional[Text] = PLUS_TEXT,
            minus: Optional[Text] = MINUS_TEXT,
            text: Optional[Text] = DEFAULT_COUNTER_TEXT,
            min_value: float = 0,
            max_value: float = 999999,
            increment: float = 1,
            default: float = 0,
            cycle: bool = False,
            on_click: OnCounterEventVariant = None,
            on_text_click: OnCounterEventVariant = None,
            on_value_changed: OnCounterEventVariant = None,
            when: WhenCondition = None,
    ) -> None:
        """
        Init counter widget.

        :param id: ID of widget
        :param plus: Text to render `+`-button. Set `None` to disable
        :param minus: Text to render `-`-button. Set `None` to disable
        :param text: Text to render button with current value. \
        Set `None` to disable
        :param min_value: Minimal allowed value
        :param max_value: Maximum allowed value
        :param increment: Step used to increment
        :param default: Default value
        :param cycle: Whether cycle values on overflow
        :param on_click: Callback to process any click
        :param on_text_click: Callback to process click on `text`-button
        :param on_value_changed: Callback to process value changes, \
        regardless of the reason
        :param when: Condition when to show widget
        """
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
        self.on_text_click = ensure_event_processor(on_text_click)

    def get_value(self, manager: DialogManager) -> float:
        return self.get_widget_data(manager, self.default)

    async def set_value(self, manager: DialogManager,
                        value: float) -> None:
        if self.min <= value <= self.max:
            self.set_widget_data(manager, value)
            await self.on_value_changed.process_event(
                manager.event,
                self.managed(manager),
                manager,
            )

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        row = []
        if self.minus:
            minus = await self.minus.render_text(data, manager)
            row.append(
                InlineKeyboardButton(
                    text=minus,
                    callback_data=self._item_callback_data("-"),
                ),
            )
        if self.text:
            text = await self.text.render_text(
                {"value": self.get_value(manager), "data": data},
                manager,
            )
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=self._item_callback_data(""),
                ),
            )
        if self.plus:
            plus = await self.plus.render_text(data, manager)
            row.append(
                InlineKeyboardButton(
                    text=plus,
                    callback_data=self._item_callback_data("+"),
                ),
            )
        return [row]

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        await self.on_click.process_event(
            callback, self.managed(manager), manager,
        )

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
        elif data == "":
            await self.on_text_click.process_event(
                callback, self.managed(manager), manager,
            )
        return True

    def managed(self, manager: DialogManager):
        return ManagedCounter(self, manager)


class ManagedCounter(ManagedWidget[Counter]):
    def get_value(self) -> float:
        """Get current value set in counter."""
        return self.widget.get_value(self.manager)

    async def set_value(self, value: float) -> None:
        """Change current counter value."""
        await self.widget.set_value(self.manager, value)
