from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Optional, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.text import Case, Text
from aiogram_dialog.widgets.widget_event import (
    WidgetEventProcessor,
    ensure_event_processor,
)

from .base import Keyboard

OnStateChanged = Callable[
    [ChatEvent, "ManagedCheckbox", DialogManager], Awaitable,
]
OnStateChangedVariant = Union[
    OnStateChanged, WidgetEventProcessor, None,
]


class BaseCheckbox(Keyboard, ABC):
    def __init__(
            self,
            checked_text: Text,
            unchecked_text: Text,
            id: str,
            on_click: OnStateChangedVariant = None,
            on_state_changed: OnStateChangedVariant = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.text = Case(
            {True: checked_text, False: unchecked_text},
            selector=self._is_text_checked,
        )
        self.on_click = ensure_event_processor(on_click)
        self.on_state_changed = ensure_event_processor(on_state_changed)

    async def _render_keyboard(
            self, data: dict, manager: DialogManager,
    ) -> RawKeyboard:
        checked = int(self.is_checked(manager))
        # store current checked status in callback data
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    callback_data=self._item_callback_data(checked),
                ),
            ],
        ]

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        # remove prefix and cast "0" as False, "1" as True
        checked = data != "0"
        await self.on_click.process_event(
            callback, self.managed(manager), manager,
        )
        await self.set_checked(callback, not checked, manager)
        return True

    def _is_text_checked(
            self, data: dict, case: Case, manager: DialogManager,
    ) -> bool:
        del data  # unused
        del case  # unused
        return self.is_checked(manager)

    @abstractmethod
    def is_checked(self, manager: DialogManager) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def set_checked(
            self, event: ChatEvent, checked: bool,
            manager: DialogManager,
    ):
        raise NotImplementedError


class Checkbox(BaseCheckbox):
    def __init__(
            self,
            checked_text: Text,
            unchecked_text: Text,
            id: str,
            on_click: Union[OnStateChanged, WidgetEventProcessor, None] = None,
            on_state_changed: Optional[OnStateChanged] = None,
            default: bool = False,
            when: WhenCondition = None,
    ):
        super().__init__(
            checked_text=checked_text, unchecked_text=unchecked_text,
            on_click=on_click, on_state_changed=on_state_changed,
            id=id, when=when,
        )
        self.default = default

    def is_checked(self, manager: DialogManager) -> bool:
        return self.get_widget_data(manager, self.default)

    async def set_checked(
            self, event: ChatEvent, checked: bool,
            manager: DialogManager,
    ) -> None:
        self.set_widget_data(manager, checked)
        await self.on_state_changed.process_event(
            event, self.managed(manager), manager,
        )

    def managed(self, manager: DialogManager) -> "ManagedCheckbox":
        return ManagedCheckbox(self, manager)


class ManagedCheckbox(ManagedWidget[Checkbox]):
    def is_checked(self) -> bool:
        return self.widget.is_checked(self.manager)

    async def set_checked(self, checked: bool) -> None:
        return await self.widget.set_checked(
            self.manager.event, checked, self.manager,
        )
