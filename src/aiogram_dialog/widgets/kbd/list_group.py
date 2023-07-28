from operator import itemgetter
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton

from magic_filter import MagicFilter

from aiogram_dialog.api.internal import Widget
from aiogram_dialog.api.protocols import (
    DialogManager, DialogProtocol,
)
from aiogram_dialog.manager.sub_manager import SubManager
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from .base import Keyboard

ItemsGetter = Callable[[Dict], Sequence]
ItemIdGetter = Callable[[Any], Union[str, int]]


def get_identity(items: Sequence) -> ItemsGetter:
    def identity(data) -> Sequence:
        return items

    return identity


def get_magic_getter(f: MagicFilter) -> ItemsGetter:
    def items_magic(data: Dict) -> Sequence:
        items = f.resolve(data)
        if isinstance(items, Sequence):
            return items
        else:
            return []

    return items_magic


class ListGroup(Keyboard):
    def __init__(
            self,
            *buttons: Keyboard,
            id: Optional[str] = None,
            item_id_getter: ItemIdGetter,
            items: Union[str, ItemsGetter, MagicFilter, Sequence],
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.buttons = buttons
        self.item_id_getter = item_id_getter
        if isinstance(items, str):
            self.items_getter = itemgetter(items)
        elif isinstance(items, MagicFilter):
            self.items_getter = get_magic_getter(items)
        elif isinstance(items, Callable):
            self.items_getter = items
        else:
            self.items_getter = get_identity(items)

    async def _render_keyboard(
            self, data: Dict, manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        kbd: List[List[InlineKeyboardButton]] = []
        for pos, item in enumerate(self.items_getter(data)):
            kbd.extend(await self._render_item(pos, item, data, manager))
        return kbd

    async def _render_item(
            self,
            pos: int,
            item: Any,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        kbd: List[List[InlineKeyboardButton]] = []
        data = {"data": data, "item": item, "pos": pos + 1, "pos0": pos}
        item_id = str(self.item_id_getter(item))
        sub_manager = SubManager(
            widget=self,
            manager=manager,
            widget_id=self.widget_id,
            item_id=item_id,
        )
        for b in self.buttons:
            b_kbd = await b.render_keyboard(data, sub_manager)
            for row in b_kbd:
                for btn in row:
                    if btn.callback_data:
                        btn.callback_data = self._item_callback_data(
                            f"{item_id}:{btn.callback_data}",
                        )
            kbd.extend(b_kbd)
        return kbd

    def find(self, widget_id: str) -> Optional[Widget]:
        if widget_id == self.widget_id:
            return self
        for btn in self.buttons:
            widget = btn.find(widget_id)
            if widget:
                return widget
        return None

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        item_id, callback_data = data.split(":", maxsplit=1)
        c_vars = vars(callback)
        c_vars["data"] = callback_data
        callback = CallbackQuery(**c_vars)
        sub_manager = SubManager(
            widget=self,
            manager=manager,
            widget_id=self.widget_id,
            item_id=item_id,
        )
        for b in self.buttons:
            if await b.process_callback(callback, dialog, sub_manager):
                return True

    def managed(self, manager: DialogManager):
        return ManagedListGroupAdapter(self, manager)


class ManagedListGroupAdapter(ManagedWidget[ListGroup]):
    def find_for_item(self, widget_id: str, item_id: str) -> Optional[Any]:
        widget = self.widget.find(widget_id)
        if widget:
            return widget.managed(
                SubManager(
                    widget=self.widget,
                    manager=self.manager,
                    widget_id=self.widget.widget_id,
                    item_id=item_id,
                ),
            )
        return None
