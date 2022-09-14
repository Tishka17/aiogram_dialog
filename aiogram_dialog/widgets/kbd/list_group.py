import dataclasses
from operator import itemgetter
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton, Message

from aiogram_dialog.api.entities import Context, Stack
from aiogram_dialog.api.protocols import (
    DialogManager, DialogProtocol,
)
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from .base import Keyboard
from ...api.internal import Widget


class SubManager(DialogManager):
    # FIXME other methods
    def __init__(
            self,
            list_group: "ListGroup",
            manager: DialogManager,
            widget_id: str,
            item_id: str,
    ):
        self.list_group = list_group
        self.manager = manager
        self.widget_id = widget_id
        self.item_id = item_id

    @property
    def dialog_data(self) -> Dict:
        """Dialog data for current context."""
        return self.current_context().dialog_data

    @property
    def start_data(self) -> Dict:
        """Start data for current context."""
        return self.current_context().start_data

    def current_context(self) -> Optional[Context]:
        context = self.manager.current_context()
        data = context.widget_data.setdefault(self.widget_id, {})
        row_data = data.setdefault(self.item_id, {})
        return dataclasses.replace(context, widget_data=row_data)

    def is_preview(self) -> bool:
        return self.manager.is_preview()

    def current_stack(self) -> Optional[Stack]:
        return self.manager.current_stack()

    async def close_manager(self) -> None:
        return await self.manager.close_manager()

    async def show(self) -> Message:
        return await self.manager.show()

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        return await self.manager.reset_stack(remove_keyboard)

    async def load_data(self) -> Dict:
        return await self.manager.load_data()

    def find(self, widget_id) -> Optional[Any]:
        widget = self.list_group.find(widget_id)
        if not widget:
            return None
        return widget.managed(self)

    def find_in_parent(self, widget_id) -> Optional[Any]:
        return self.manager.find(widget_id)


ItemsGetter = Callable[[Dict], Sequence]
ItemIdGetter = Callable[[Any], Union[str, int]]


def get_identity(items: Sequence) -> ItemsGetter:
    def identity(data) -> Sequence:
        return items

    return identity


class ListGroup(Keyboard):
    def __init__(
            self,
            *buttons: Keyboard,
            id: Optional[str] = None,
            item_id_getter: ItemIdGetter,
            items: Union[str, Sequence],
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.buttons = buttons
        self.item_id_getter = item_id_getter
        if isinstance(items, str):
            self.items_getter = itemgetter(items)
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
            list_group=self, manager=manager,
            widget_id=self.widget_id, item_id=item_id,
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
            list_group=self, manager=manager,
            widget_id=self.widget_id, item_id=item_id,
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
                    self.widget,
                    self.manager,
                    self.widget.widget_id,
                    item_id,
                ),
            )
        return None
