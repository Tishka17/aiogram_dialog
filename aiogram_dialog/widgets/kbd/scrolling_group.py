from typing import List, Dict, Optional, Callable, Awaitable, Union

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.context.events import ChatEvent
from aiogram_dialog.deprecation_utils import manager_deprecated
from aiogram_dialog.manager.protocols import DialogManager, ManagedDialogProto
from aiogram_dialog.context.events import ChatEvent
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor, ensure_event_processor
from .base import Keyboard
from .group import Group
from ..managed import ManagedWidgetAdapter
from ..when import WhenCondition

OnStateChanged = Callable[
    [ChatEvent, "ManagedScrollingGroupAdapter", DialogManager],
    Awaitable,
]


class ScrollingGroup(Group):
    def __init__(self, *buttons: Keyboard, id: str, width: Optional[int] = None,
                 height: int = 0, when: WhenCondition = None,
                 on_page_changed: Union[OnStateChanged, WidgetEventProcessor, None] = None):
        super().__init__(*buttons, id=id, width=width, when=when)
        self.height = height
        self.on_page_changed = ensure_event_processor(on_page_changed)

    async def _render_keyboard(
            self, data: Dict, manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        kbd = await super()._render_keyboard(data, manager)
        pages = len(kbd) // self.height + bool(len(kbd) % self.height)
        last_page = pages - 1
        if pages == 0:
            return kbd
        current_page = min(last_page, self.get_page(manager))
        next_page = min(last_page, current_page + 1)
        prev_page = max(0, current_page - 1)
        pager = [[
            InlineKeyboardButton(
                text="1", callback_data=self._item_callback_data("0")
            ),
            InlineKeyboardButton(
                text="<", callback_data=self._item_callback_data(prev_page),
            ),
            InlineKeyboardButton(
                text=str(current_page + 1),
                callback_data=self._item_callback_data(current_page),
            ),
            InlineKeyboardButton(
                text=">", callback_data=self._item_callback_data(next_page),
            ),
            InlineKeyboardButton(
                text=str(last_page + 1),
                callback_data=self._item_callback_data(last_page),
            ),
        ]]
        page_offset = current_page * self.height
        return kbd[page_offset:page_offset + self.height] + pager

    async def _process_item_callback(
            self, c: CallbackQuery, data: str, dialog: ManagedDialogProto,
            manager: DialogManager,
    ) -> bool:
        await self.set_page(c, int(data), manager)
        return True

    def get_page(self, manager: DialogManager) -> int:
        return manager.current_context().widget_data.get(self.widget_id, 0)

    async def set_page(self, event: ChatEvent, page: int,
                       manager: DialogManager) -> None:
        manager.current_context().widget_data[self.widget_id] = page
        await self.on_page_changed.process_event(
            event, self.managed(manager), manager,
        )

    def managed(self, manager: DialogManager):
        return ManagedScrollingGroupAdapter(self, manager)


class ManagedScrollingGroupAdapter(ManagedWidgetAdapter[ScrollingGroup]):
    def get_page(self, manager: Optional[DialogManager] = None) -> int:
        manager_deprecated(manager)
        return self.widget.get_page(self.manager)

    async def set_page(self, event: ChatEvent, page: int,
                       manager: Optional[DialogManager] = None) -> None:
        manager_deprecated(manager)
        return await self.widget.set_page(
            event, page, self.manager
        )
