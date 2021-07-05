from typing import List, Dict, Optional, Callable, Awaitable, Union

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog, ChatEvent
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor, ensure_event_processor
from .base import Keyboard
from .group import Group
from ..when import WhenCondition

# Constants for navigating pages with buttons
PAGE_NEXT = "+"
PAGE_PREV = "-"

OnStateChanged = Callable[[ChatEvent, "ScrollingGroup", DialogManager], Awaitable]


class ScrollingGroup(Group):
    def __init__(self, *buttons: Keyboard, id: Optional[str] = None, width: Optional[int] = None,
                 height: int = 0, when: WhenCondition = None,
                 on_page_changed: Union[OnStateChanged, WidgetEventProcessor, None] = None):
        super().__init__(*buttons, id=id, width=width, when=when)
        self.height = height
        self.on_page_changed = ensure_event_processor(on_page_changed)

    async def _render_keyboard(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        kbd = await super()._render_keyboard(data, manager)
        pages = len(kbd) // self.height + bool(len(kbd) % self.height)
        last_page = pages - 1
        if pages == 0:
            return kbd
        current_page = min(last_page, self.get_page(manager))
        pager = [[
            InlineKeyboardButton(text="1", callback_data=f"{self.widget_id}:0"),
            InlineKeyboardButton(text="<", callback_data=f"{self.widget_id}:{PAGE_PREV}"),
            InlineKeyboardButton(text=str(current_page + 1), callback_data=f"{self.widget_id}:{current_page}"),
            InlineKeyboardButton(text=">", callback_data=f"{self.widget_id}:{PAGE_NEXT}"),
            InlineKeyboardButton(text=str(last_page + 1), callback_data=f"{self.widget_id}:{last_page}"),
        ]]
        return kbd[current_page * self.height: (current_page + 1) * self.height] + pager

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        prefix = f"{self.widget_id}:"
        if not c.data.startswith(prefix):
            return await super().process_callback(c, dialog, manager)
        data = c.data[len(prefix):]
        page = self.get_page(manager)

        if data == PAGE_NEXT:
            await self.set_page(c, page + 1, manager)
        elif data == PAGE_PREV:
            await self.set_page(c, max(0, page - 1), manager)
        else:
            new_page = int(data)
            await self.set_page(c, new_page, manager)
        return True

    def get_page(self, manager: DialogManager) -> int:
        return manager.current_context().widget_data.get(self.widget_id, 0)

    async def set_page(self, event: ChatEvent, page: int, manager: DialogManager):
        manager.current_context().widget_data[self.widget_id] = page
        await self.on_page_changed.process_event(event, self, manager)
