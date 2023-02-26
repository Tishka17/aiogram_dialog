from typing import Awaitable, Callable, Dict, List, Optional, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import (
    ManagedScroll, Scroll, WhenCondition,
)
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor,
    WidgetEventProcessor,
)
from .base import Keyboard
from .group import Group

OnStateChanged = Callable[
    [ChatEvent, ManagedScroll, DialogManager],
    Awaitable,
]


class ScrollingGroup(Group, Scroll):
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
            hide_pager: bool = False,
    ):
        super().__init__(*buttons, id=id, width=width, when=when)
        self.height = height
        self.on_page_changed = ensure_event_processor(on_page_changed)
        self.hide_on_single_page = hide_on_single_page
        self.hide_pager = hide_pager

    def _get_page_count(
            self,
            keyboard: List[List[InlineKeyboardButton]],
    ) -> int:
        return len(keyboard) // self.height + bool(len(keyboard) % self.height)

    async def _render_contents(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return await super()._render_keyboard(data, manager)

    async def _render_pager(
            self,
            pages: int,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        if self.hide_pager:
            return []
        if pages == 0 or (pages == 1 and self.hide_on_single_page):
            return []

        last_page = pages - 1
        current_page = min(last_page, await self.get_page(manager))
        next_page = min(last_page, current_page + 1)
        prev_page = max(0, current_page - 1)

        return [
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

    async def _render_page(
            self,
            page: int,
            keyboard: List[List[InlineKeyboardButton]],
    ) -> List[List[InlineKeyboardButton]]:
        pages = self._get_page_count(keyboard)
        last_page = pages - 1
        current_page = min(last_page, page)
        page_offset = current_page * self.height

        return keyboard[page_offset: page_offset + self.height]

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        keyboard = await self._render_contents(data, manager)
        pages = self._get_page_count(keyboard)

        pager = await self._render_pager(pages, manager)
        page_keyboard = await self._render_page(
            page=await self.get_page(manager),
            keyboard=keyboard,
        )

        return page_keyboard + pager

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        await self.set_page(callback, int(data), manager)
        return True

    async def get_page_count(self, data: Dict, manager: DialogManager) -> int:
        keyboard = await self._render_contents(data, manager)
        return self._get_page_count(keyboard=keyboard)

    async def get_page(self, manager: DialogManager) -> int:
        return self.get_widget_data(manager, 0)

    async def set_page(
            self, event: ChatEvent, page: int, manager: DialogManager,
    ) -> None:
        self.set_widget_data(manager, page)
        await self.on_page_changed.process_event(
            event,
            self.managed(manager),
            manager,
        )

    def managed(self, manager: DialogManager):
        return ManagedScroll(self, manager)
