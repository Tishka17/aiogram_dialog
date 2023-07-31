from abc import ABC, abstractmethod
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
)

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.text import Case, Text
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor,
    WidgetEventProcessor,
)
from .base import Keyboard
from ..common.items import get_items_getter, ItemsGetterVariant

T = TypeVar("T")
TypeFactory = Callable[[str], T]
ItemIdGetter = Callable[[Any], Union[str, int]]
OnItemStateChanged = Callable[
    [ChatEvent, ManagedWidget["Select"], DialogManager, T],
    Awaitable,
]
OnItemClick = Callable[
    [CallbackQuery, ManagedWidget["Select"], DialogManager, T],
    Awaitable,
]


class Select(Keyboard, Generic[T]):
    def __init__(
            self,
            text: Text,
            id: str,
            item_id_getter: ItemIdGetter,
            items: ItemsGetterVariant,
            type_factory: TypeFactory[T] = str,
            on_click: Union[OnItemClick[T], WidgetEventProcessor, None] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.text = text
        self.type_factory = type_factory
        self.on_click = ensure_event_processor(on_click)
        self.item_id_getter = item_id_getter
        self.items_getter = get_items_getter(items)

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [
            [
                await self._render_button(pos, item, data, manager)
                for pos, item in enumerate(self.items_getter(data))
            ],
        ]

    async def _render_button(
            self, pos: int, item: Any, data: Dict,
            manager: DialogManager,
    ) -> InlineKeyboardButton:
        data = {"data": data, "item": item, "pos": pos + 1, "pos0": pos}
        item_id = self.item_id_getter(item)
        return InlineKeyboardButton(
            text=await self.text.render_text(data, manager),
            callback_data=self._item_callback_data(item_id),
        )

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        await self.on_click.process_event(
            callback,
            self.managed(manager),
            manager,
            self.type_factory(data),
        )
        return True


class StatefulSelect(Select[T], ABC, Generic[T]):
    def __init__(
            self,
            checked_text: Text,
            unchecked_text: Text,
            id: str,
            item_id_getter: ItemIdGetter,
            items: ItemsGetterVariant,
            type_factory: TypeFactory[T] = str,
            on_click: Union[OnItemClick[T], WidgetEventProcessor, None] = None,
            on_state_changed: Union[
                OnItemStateChanged[T], WidgetEventProcessor, None,
            ] = None,
            when: Union[str, Callable] = None,
    ):
        text = Case(
            {True: checked_text, False: unchecked_text},
            selector=self._is_text_checked,
        )
        super().__init__(
            text=text,
            item_id_getter=item_id_getter, items=items,
            on_click=self._process_click,
            id=id, when=when, type_factory=type_factory,
        )
        self.on_item_click = ensure_event_processor(on_click)
        self.on_state_changed = ensure_event_processor(on_state_changed)

    async def _process_on_state_changed(
            self, event: ChatEvent, item_id: str, manager: DialogManager,
    ):
        if self.on_state_changed:
            await self.on_state_changed.process_event(
                event, self.managed(manager), manager,
                self.type_factory(item_id),
            )

    @abstractmethod
    def _is_text_checked(
            self, data: Dict, case: Case, manager: DialogManager,
    ) -> bool:
        raise NotImplementedError

    async def _process_click(
            self,
            callback: CallbackQuery,
            select: ManagedWidget[Select],
            manager: DialogManager,
            item_id: str,
    ):
        if self.on_item_click:
            await self.on_item_click.process_event(
                callback, select, manager, self.type_factory(item_id),
            )
        await self._on_click(callback, select, manager, str(item_id))

    @abstractmethod
    async def _on_click(
            self,
            callback: CallbackQuery,
            select: ManagedWidget[Select],
            manager: DialogManager,
            item_id: str,
    ):
        raise NotImplementedError


class Radio(StatefulSelect[T], Generic[T]):
    def get_checked(self, manager: DialogManager) -> Optional[str]:
        return self.get_widget_data(manager, None)

    async def set_checked(
            self, event: ChatEvent, item_id: Optional[str],
            manager: DialogManager,
    ):
        checked = self.get_checked(manager)
        self.set_widget_data(manager, item_id)
        if checked != item_id:
            await self._process_on_state_changed(event, item_id, manager)

    def is_checked(
            self, item_id: Union[str, int], manager: DialogManager,
    ) -> bool:
        return str(item_id) == self.get_checked(manager)

    def _preview_checked_id(
            self, manager: DialogManager, item_id: str,
    ) -> str:
        return self.get_widget_data(manager, item_id)

    def _is_text_checked(
            self, data: Dict, case: Case, manager: DialogManager,
    ) -> bool:
        item_id = str(self.item_id_getter(data["item"]))
        if manager.is_preview():
            return item_id == self._preview_checked_id(manager, item_id)
        return self.is_checked(item_id, manager)

    async def _on_click(
            self,
            callback: CallbackQuery,
            select: Select,
            manager: DialogManager,
            item_id: str,
    ):
        await self.set_checked(callback, item_id, manager)

    def managed(self, manager: DialogManager):
        return ManagedRadioAdapter(self, manager)


class ManagedRadioAdapter(ManagedWidget[Radio]):
    def get_checked(self) -> Optional[str]:
        return self.widget.get_checked(self.manager)

    async def set_checked(self, item_id: Optional[str]):
        return await self.widget.set_checked(
            self.manager.event, item_id, self.manager,
        )

    def is_checked(
            self, item_id: Union[str, int],
    ) -> bool:
        return self.widget.is_checked(item_id, self.manager)


class Multiselect(StatefulSelect[T], Generic[T]):
    def __init__(
            self,
            checked_text: Text,
            unchecked_text: Text,
            id: str,
            item_id_getter: ItemIdGetter,
            items: ItemsGetterVariant,
            min_selected: int = 0,
            max_selected: int = 0,
            type_factory: TypeFactory[T] = str,
            on_click: Union[OnItemClick[T], WidgetEventProcessor, None] = None,
            on_state_changed: Union[
                OnItemStateChanged[T], WidgetEventProcessor, None,
            ] = None,
            when: Union[str, Callable] = None,
    ):
        super().__init__(
            checked_text=checked_text,
            unchecked_text=unchecked_text,
            item_id_getter=item_id_getter,
            items=items,
            on_click=on_click,
            on_state_changed=on_state_changed,
            id=id, when=when, type_factory=type_factory,
        )
        self.min_selected = min_selected
        self.max_selected = max_selected

    def _is_text_checked(
            self, data: Dict, case: Case, manager: DialogManager,
    ) -> bool:
        item_id = str(self.item_id_getter(data["item"]))
        if manager.is_preview():
            return (
                # just stupid way to make it differ in preview
                ord(item_id[-1]) % 2 == 1
            )
        return self.is_checked(item_id, manager)

    def is_checked(
            self, item_id: Union[str, int], manager: DialogManager,
    ) -> bool:
        data: List = self.get_checked(manager)
        return str(item_id) in data

    def get_checked(self, manager: DialogManager) -> List[str]:
        return self.get_widget_data(manager, [])

    async def reset_checked(
            self, event: ChatEvent, manager: DialogManager,
    ) -> None:
        self.set_widget_data(manager, [])

    async def set_checked(
            self,
            event: ChatEvent,
            item_id: str,
            checked: bool,
            manager: DialogManager,
    ) -> None:
        data: List = self.get_checked(manager)
        changed = False
        if item_id in data:
            if not checked:
                if len(data) > self.min_selected:
                    data.remove(item_id)
                    changed = True
        else:
            if checked:
                if self.max_selected == 0 or self.max_selected > len(data):
                    data.append(item_id)
                    changed = True
        if changed:
            self.set_widget_data(manager, data)
            await self._process_on_state_changed(event, item_id, manager)

    async def _on_click(
            self,
            callback: CallbackQuery,
            select: Select,
            manager: DialogManager,
            item_id: str,
    ):
        await self.set_checked(
            callback, item_id, not self.is_checked(item_id, manager), manager,
        )

    def managed(self, manager: DialogManager):
        return ManagedMultiSelectAdapter(self, manager)


class ManagedMultiSelectAdapter(ManagedWidget[Multiselect]):
    def is_checked(
            self, item_id: Union[str, int],
    ) -> bool:
        return self.widget.is_checked(item_id, self.manager)

    def get_checked(self) -> List[str]:
        return self.widget.get_checked(self.manager)

    async def reset_checked(self):
        return await self.widget.reset_checked(
            self.manager.event, self.manager,
        )

    async def set_checked(self, item_id: str, checked: bool) -> None:
        return await self.widget.set_checked(
            self.manager.event, item_id, checked, self.manager,
        )
