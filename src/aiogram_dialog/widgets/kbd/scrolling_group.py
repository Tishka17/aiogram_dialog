from typing import Awaitable, Callable, Dict, List, Optional, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor,
    WidgetEventProcessor,
)
from .base import Keyboard
from .group import Group

OnStateChanged = Callable[
    [ChatEvent, "ManagedScrollingGroupAdapter", DialogManager],
    Awaitable,
]


class ScrollingGroup(Group):
    def __init__(
            self,
            *buttons: Keyboard,
            id: str,
            width: Optional[int] = None,
            height: int = 0,
            when: WhenCondition = None,
            on_page_changed: Union[
                OnStateChanged, WidgetEventProcessor, None,
            ] = None,
            hide_on_single_page: bool = False,
    ):
        super().__init__(*buttons, id=id, width=width, when=when)
        self.height = height
        self.on_page_changed = ensure_event_processor(on_page_changed)
        self.hide_on_single_page = hide_on_single_page

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        kbd = await super()._render_keyboard(data, manager)
        pages = len(kbd) // self.height + bool(len(kbd) % self.height)
        last_page = pages - 1
        if pages == 0 or (pages == 1 and self.hide_on_single_page):
            return kbd
        current_page = min(last_page, self.get_page(manager))
        next_page = min(last_page, current_page + 1)
        prev_page = max(0, current_page - 1)
        pager = [
            [
                InlineKeyboardButton(
                    text="1", callback_data=self._item_callback_data("0"),
                ),
                InlineKeyboardButton(
                    text="<",
                    callback_data=self._item_callback_data(prev_page),
                ),
                InlineKeyboardButton(
                    text=str(current_page + 1),
                    callback_data=self._item_callback_data(current_page),
                ),
                InlineKeyboardButton(
                    text=">",
                    callback_data=self._item_callback_data(next_page),
                ),
                InlineKeyboardButton(
                    text=str(last_page + 1),
                    callback_data=self._item_callback_data(last_page),
                ),
            ],
        ]
        page_offset = current_page * self.height
        return kbd[page_offset: page_offset + self.height] + pager

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        await self.set_page(callback, int(data), manager)
        return True

    def get_page(self, manager: DialogManager) -> int:
        return manager.current_context().widget_data.get(self.widget_id, 0)

    async def set_page(
            self, event: ChatEvent, page: int, manager: DialogManager,
    ) -> None:
        manager.current_context().widget_data[self.widget_id] = page
        await self.on_page_changed.process_event(
            event,
            self.managed(manager),
            manager,
        )

    def managed(self, manager: DialogManager):
        return ManagedScrollingGroupAdapter(self, manager)


class ManagedScrollingGroupAdapter(ManagedWidget[ScrollingGroup]):
    def get_page(self) -> int:
        return self.widget.get_page(self.manager)

    async def set_page(self, page: int) -> None:
        return await self.widget.set_page(
            self.manager.event, page, self.manager,
        )
