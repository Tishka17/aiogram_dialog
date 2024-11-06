from collections.abc import Callable
from typing import Any, Optional, Union

from aiogram.types import CallbackQuery

from aiogram_dialog.api.internal import RawKeyboard, Widget
from aiogram_dialog.api.protocols import (
    DialogManager,
    DialogProtocol,
)
from aiogram_dialog.manager.sub_manager import SubManager
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.common.items import (
    ItemsGetterVariant,
    get_items_getter,
)

from .base import Keyboard

ItemIdGetter = Callable[[Any], Union[str, int]]


class ListGroup(Keyboard):
    def __init__(
            self,
            *buttons: Keyboard,
            id: str,
            item_id_getter: ItemIdGetter,
            items: ItemsGetterVariant,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.buttons = buttons
        self.item_id_getter = item_id_getter
        self.items_getter = get_items_getter(items)

    async def _render_keyboard(
            self, data: dict, manager: DialogManager,
    ) -> RawKeyboard:
        kbd: RawKeyboard = []
        for pos, item in enumerate(self.items_getter(data)):
            kbd.extend(await self._render_item(pos, item, data, manager))
        return kbd

    async def _render_item(
            self,
            pos: int,
            item: Any,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        kbd: RawKeyboard = []
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
        callback = callback.model_copy(update={
            "data": callback_data,
        })
        sub_manager = SubManager(
            widget=self,
            manager=manager,
            widget_id=self.widget_id,
            item_id=item_id,
        )
        for b in self.buttons:  # noqa: RET503
            if await b.process_callback(callback, dialog, sub_manager):
                return True

    def managed(self, manager: DialogManager) -> "ManagedListGroup":
        return ManagedListGroup(self, manager)


class ManagedListGroup(ManagedWidget[ListGroup]):
    def find_for_item(self, widget_id: str, item_id: str) -> Optional[Any]:
        """Find widget for specific item_id."""
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
