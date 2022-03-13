import dataclasses
from operator import itemgetter
from typing import List, Dict, Optional, Union, Sequence, Callable, Any, cast

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager, Context
from .base import Keyboard
from ..when import WhenCondition


class SubManager:
    def __init__(
            self,
            manager: DialogManager,
            widget_id: str,
            item_id: str,
    ):
        self.manager = manager
        self.widget_id = widget_id
        self.item_id = item_id

    def current_context(self) -> Optional[Context]:
        context = self.manager.current_context()
        data = context.widget_data.setdefault(self.widget_id, {})
        row_data = data.setdefault(self.item_id, {})
        return dataclasses.replace(context, widget_data=row_data)

    def __getattr__(self, item):
        return getattr(self.manager, item)


ItemsGetter = Callable[[Dict], Sequence]
ItemIdGetter = Callable[[Any], Union[str, int]]


def get_identity(items: Sequence) -> ItemsGetter:
    def identity(data) -> Sequence:
        return items

    return identity


class ListGroup(Keyboard):
    def __init__(
            self, *buttons: Keyboard,
            id: Optional[str] = None,
            item_id_getter: ItemIdGetter,
            items: Union[str, Sequence],
            when: WhenCondition = None,
    ):
        super().__init__(id, when)
        self.buttons = buttons
        self.item_id_getter = item_id_getter
        if isinstance(items, str):
            self.items_getter = itemgetter(items)
        else:
            self.items_getter = get_identity(items)

    async def _render_keyboard(
            self, data: Dict, manager: DialogManager
    ) -> List[List[InlineKeyboardButton]]:
        kbd: List[List[InlineKeyboardButton]] = []
        for pos, item in enumerate(self.items_getter(data)):
            kbd.extend(await self._render_item(pos, item, data, manager))
        return kbd

    async def _render_item(
            self, pos: int, item: Any, data: Dict, manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        kbd: List[List[InlineKeyboardButton]] = []
        data = {"data": data, "item": item, "pos": pos + 1, "pos0": pos}
        item_id = str(self.item_id_getter(item))
        for b in self.buttons:
            b_kbd = await b.render_keyboard(data, manager)
            for row in b_kbd:
                for btn in row:
                    if btn.callback_data:
                        btn.callback_data = (
                            f"{self.widget_id}:"
                            f"{item_id}:"
                            f"{btn.callback_data}"
                        )
            kbd.extend(b_kbd)
        return kbd

    async def process_callback(
            self, c: CallbackQuery, dialog: Dialog, manager: DialogManager
    ) -> bool:
        if not c.data.startswith(f"{self.widget_id}:"):
            return False
        widget_id, item_id, callback_data = c.data.split(":", maxsplit=2)
        c_vars = vars(c)
        c_vars["data"] = callback_data
        c = CallbackQuery(**c_vars)
        for b in self.buttons:
            sub_manager = cast(SubManager(manager, widget_id, item_id),
                               DialogManager)
            if await b.process_callback(c, dialog, sub_manager):
                return True
