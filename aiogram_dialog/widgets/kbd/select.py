from abc import ABC, abstractmethod
from operator import itemgetter
from typing import Callable, Optional, Union, Dict, Any, List, Awaitable, Sequence

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.context.events import ChatEvent
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Text, Case
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor, ensure_event_processor
from .base import Keyboard

ItemIdGetter = Callable[[Any], Union[str, int]]
ItemsGetter = Callable[[Dict], Sequence]
OnItemStateChanged = Callable[[ChatEvent, "Select", DialogManager, str], Awaitable]
OnItemClick = Callable[[CallbackQuery, "Select", DialogManager, str], Awaitable]


def get_identity(items: Sequence) -> ItemsGetter:
    def identity(data) -> Sequence:
        return items

    return identity


class Select(Keyboard):
    def __init__(self, text: Text,
                 id: str,
                 item_id_getter: ItemIdGetter,
                 items: Union[str, Sequence],
                 on_click: Union[OnItemClick, WidgetEventProcessor, None] = None,
                 when: Union[str, Callable] = None):
        super().__init__(id, when)
        self.text = text
        self.widget_id = id
        self.on_click = ensure_event_processor(on_click)
        self.callback_data_prefix = id + ":"
        self.item_id_getter = item_id_getter
        if isinstance(items, str):
            self.items_getter = itemgetter(items)
        else:
            self.items_getter = get_identity(items)

    async def _render_keyboard(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
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
        await self.on_click.process_event(c, self, manager, item_id)
        return True


class StatefulSelect(Select, ABC):
    def __init__(self, checked_text: Text, unchecked_text: Text,
                 id: str, item_id_getter: ItemIdGetter,
                 items: Union[str, Sequence],
                 on_click: Union[OnItemClick, WidgetEventProcessor, None] = None,
                 on_state_changed: Union[OnItemStateChanged, WidgetEventProcessor, None] = None,
                 when: Union[str, Callable] = None):
        text = Case({True: checked_text, False: unchecked_text}, selector=self._is_text_checked)
        super().__init__(text, id, item_id_getter, items, self._process_click, when)
        self.on_item_click = ensure_event_processor(on_click)
        self.on_state_changed = ensure_event_processor(on_state_changed)

    async def _process_on_state_changed(self, event: ChatEvent, item_id: str, manager: DialogManager):
        if self.on_state_changed:
            await self.on_state_changed.process_event(event, self, manager, item_id)

    @abstractmethod
    def _is_text_checked(self, data: Dict, case: Case, manager: DialogManager) -> bool:
        raise NotImplementedError

    async def _process_click(self, c: CallbackQuery, select: Select, manager: DialogManager, item_id: str):
        if self.on_item_click:
            await self.on_item_click.process_event(c, select, manager, item_id)
        await self._on_click(c, select, manager, item_id)

    @abstractmethod
    async def _on_click(self, c: CallbackQuery, select: Select, manager: DialogManager, item_id: str):
        raise NotImplementedError


class Radio(StatefulSelect):
    def get_checked(self, manager: DialogManager) -> Optional[str]:
        return manager.context.data(self.widget_id, None, internal=True)

    async def set_checked(self, event: ChatEvent, item_id: Optional[str], manager: DialogManager):
        checked = self.get_checked(manager)
        manager.context.set_data(self.widget_id, item_id, internal=True)
        if checked != item_id:
            await self._process_on_state_changed(event, item_id, manager)

    def is_checked(self, item_id: Union[str, int], manager: DialogManager) -> bool:
        return str(item_id) == self.get_checked(manager)

    def _is_text_checked(self, data: Dict, case: Case, manager: DialogManager) -> bool:
        item_id = str(self.item_id_getter(data["item"]))
        return self.is_checked(item_id, manager)

    async def _on_click(self, c: CallbackQuery, select: Select, manager: DialogManager, item_id: str):
        await self.set_checked(c, item_id, manager)


class Multiselect(StatefulSelect):
    def __init__(self, checked_text: Text, unchecked_text: Text, id: str, item_id_getter: ItemIdGetter,
                 items: Union[str, Sequence], min_selected: int = 0, max_selected: int = 0,
                 on_click: Union[OnItemClick, WidgetEventProcessor, None] = None,
                 on_state_changed: Union[OnItemStateChanged, WidgetEventProcessor, None] = None,
                 when: Union[str, Callable] = None):
        super().__init__(checked_text, unchecked_text, id, item_id_getter, items, on_click, on_state_changed, when)
        self.min_selected = min_selected
        self.max_selected = max_selected

    def _is_text_checked(self, data: Dict, case: Case, manager: DialogManager) -> bool:
        item_id = str(self.item_id_getter(data["item"]))
        return self.is_checked(item_id, manager)

    def is_checked(self, item_id: Union[str, int], manager: DialogManager) -> bool:
        data: List = self.get_checked(manager)
        return str(item_id) in data

    def get_checked(self, manager: DialogManager) -> List[str]:
        return manager.context.data(self.widget_id, [], internal=True)

    async def reset_checked(self, event: ChatEvent, manager: DialogManager):
        manager.context.set_data(self.widget_id, [], internal=True)

    async def set_checked(self, event: ChatEvent, item_id: str, checked: bool, manager: DialogManager) -> None:
        data: List = self.get_checked(manager)
        if item_id in data:
            if not checked:
                if len(data) > self.min_selected:
                    data.remove(item_id)
                    await self._process_on_state_changed(event, item_id, manager)
        else:
            if checked:
                if self.max_selected == 0 or self.max_selected > len(data):
                    data.append(item_id)
                    await self._process_on_state_changed(event, item_id, manager)
        manager.context.set_data(self.widget_id, data, internal=True)

    async def _on_click(self, c: CallbackQuery, select: Select, manager: DialogManager, item_id: str):
        await self.set_checked(c, item_id, not self.is_checked(item_id, manager), manager)
