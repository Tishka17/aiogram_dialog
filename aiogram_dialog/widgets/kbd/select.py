from operator import itemgetter
from typing import Callable, Optional, Union, Dict, Any, List, Awaitable, Sequence

from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.intent import ChatEvent
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Text, Case
from .base import Keyboard

ItemIdGetter = Callable[[Any], Union[str, int]]
ItemsGetter = Callable[[Dict], Sequence]
OnStateChanged = Callable[[CallbackQuery, str, "Select", DialogManager], Awaitable]


def get_identity(items: Sequence) -> ItemsGetter:
    def identity(data) -> Sequence:
        return items

    return identity


class Select(Keyboard):
    def __init__(self, checked_text: Text, unchecked_text: Text,
                 id: str,
                 item_id_getter: ItemIdGetter,
                 items: Union[str, Sequence],
                 multiple: bool = False,
                 min_selected: int = 0,
                 max_selected: int = 0,
                 on_state_changed: Optional[OnStateChanged] = None,
                 when: Union[str, Callable] = None):
        super().__init__(id, when)
        self.text = Case({True: checked_text, False: unchecked_text}, selector=self._is_text_checked)
        self.widget_id = id
        self.on_state_changed = on_state_changed
        self.callback_data_prefix = id + ":"
        self.item_id_getter = item_id_getter
        self.multiple = multiple
        self.min_selected = min_selected
        self.max_selected = max_selected
        if isinstance(items, str):
            self.items_getter = itemgetter(items)
        else:
            self.items_getter = get_identity(items)

    async def _render_kbd(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        return [[
            await self._render_button(pos, item, data, manager)
            for pos, item in enumerate(self.items_getter(data))
        ]]

    async def _render_button(self, pos: int, item: Any, data: Dict, manager: DialogManager) -> InlineKeyboardButton:
        data = {"data": data, "item": item, "pos": pos + 1, "pos0": pos}
        return InlineKeyboardButton(
            text=await self.text.render_text(data, manager),
            callback_data=self.callback_data_prefix + str(self.item_id_getter(item))
        )

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        if not c.data.startswith(self.callback_data_prefix):
            return False
        item_id = c.data[len(self.callback_data_prefix):]
        self.set_checked(c, item_id, not self.is_checked(item_id, manager), manager)
        return True

    def _is_text_checked(self, data: Dict, case: Case, manager: DialogManager) -> bool:
        item_id = str(self.item_id_getter(data["item"]))
        return self.is_checked(item_id, manager)

    def reset_checked(self, event: ChatEvent, manager: DialogManager):
        manager.context.set_data(self.widget_id, [], internal=True)

    def get_checked(self, manager: DialogManager) -> Optional[str]:
        data = self.get_multichecked(manager)
        if not data:
            return None
        return data[0]

    def get_multichecked(self, manager: DialogManager) -> List[str]:
        return manager.context.data(self.widget_id, [], internal=True)

    def is_checked(self, item_id: Union[str, int], manager: DialogManager) -> bool:
        data: List = self.get_multichecked(manager)
        return str(item_id) in data

    async def _process_on_state_changed(self, event: ChatEvent, item_id: str, manager: DialogManager):
        if self.on_state_changed:
            await self.on_state_changed(event, item_id, self, manager)

    def set_checked(self, event: ChatEvent, item_id: str, checked: bool, manager: DialogManager) -> None:
        data: List = self.get_multichecked(manager)
        if item_id in data:
            if not checked:
                if len(data) > self.min_selected:
                    data.remove(item_id)
                    self._process_on_state_changed(event, item_id, manager)
        else:
            if checked:
                if self.multiple:
                    if self.max_selected == 0 or self.max_selected > len(data):
                        data.append(item_id)
                        self._process_on_state_changed(event, item_id, manager)
                else:
                    data = [item_id]
                    self._process_on_state_changed(event, item_id, manager)
        manager.context.set_data(self.widget_id, data, internal=True)
