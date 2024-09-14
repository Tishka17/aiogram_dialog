from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.internal import RawKeyboard
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
ManagedT = TypeVar("ManagedT")
TypeFactory = Callable[[str], T]
ItemIdGetter = Callable[[Any], Union[str, int]]


class OnItemStateChanged(Protocol[ManagedT, T]):
    @abstractmethod
    async def __call__(
            self,
            event: ChatEvent,
            select: ManagedT,  # noqa: F841
            dialog_manager: DialogManager,
            data: T,
            /,
    ):
        raise NotImplementedError


class OnItemClick(Protocol[ManagedT, T]):
    @abstractmethod
    async def __call__(
            self,
            event: CallbackQuery,
            select: ManagedT,  # noqa: F841
            dialog_manager: DialogManager,
            data: T,
            /,
    ):
        raise NotImplementedError


class Select(Keyboard, Generic[T]):
    def __init__(
            self,
            text: Text,
            id: str,
            item_id_getter: ItemIdGetter,
            items: ItemsGetterVariant,
            type_factory: TypeFactory[T] = str,
            on_click: Union[
                OnItemClick["Select[T]", T], WidgetEventProcessor, None,
            ] = None,
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
    ) -> RawKeyboard:
        return [
            [
                await self._render_button(pos, item, item, data, manager)
                for pos, item in enumerate(self.items_getter(data))
            ],
        ]

    async def _render_button(
            self, pos: int, item: Any, target_item: Any, data: Dict,
            manager: DialogManager,
    ) -> InlineKeyboardButton:
        """
        Render one of the buttons in keyboard.

        :param pos position of the item among all of them
        :param item what to show
        :param target_item what to use for callback
        """
        data = {
            "data": data, "item": item, "target_item": target_item,
            "pos": pos + 1, "pos0": pos,
        }
        item_id = self.item_id_getter(target_item)
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
            on_click: Union[
                OnItemClick[ManagedT, T], WidgetEventProcessor, None,
            ] = None,
            on_state_changed: Union[
                OnItemStateChanged[ManagedT, T], WidgetEventProcessor, None,
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
        await self._on_click(callback, select, manager, item_id)

    @abstractmethod
    async def _on_click(
            self,
            callback: CallbackQuery,
            select: ManagedWidget[Select],
            manager: DialogManager,
            item_id: str,
    ):
        raise NotImplementedError

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
            data,
        )
        return True


class Radio(StatefulSelect[T], Generic[T]):
    def __init__(
            self,
            checked_text: Text,
            unchecked_text: Text,
            id: str,
            item_id_getter: ItemIdGetter,
            items: ItemsGetterVariant,
            type_factory: TypeFactory[T] = str,
            on_click: Union[
                OnItemClick["ManagedRadio[T]", T],
                WidgetEventProcessor, None,
            ] = None,
            on_state_changed: Union[
                OnItemStateChanged["ManagedRadio[T]", T],
                WidgetEventProcessor, None,
            ] = None,
            when: Union[str, Callable] = None,
    ):

        super().__init__(
            checked_text=checked_text,
            unchecked_text=unchecked_text,
            id=id,
            item_id_getter=item_id_getter,
            items=items,
            type_factory=type_factory,
            on_click=on_click,
            on_state_changed=on_state_changed,
            when=when,
        )

    def get_checked(self, manager: DialogManager) -> Optional[T]:
        data = self._get_checked(manager)
        if data is None:
            return None
        return self.type_factory(data)

    def _get_checked(self, manager: DialogManager) -> Optional[str]:
        return self.get_widget_data(manager, None)

    async def set_checked(
            self, event: ChatEvent, item_id: T,
            manager: DialogManager,
    ) -> None:
        checked = self._get_checked(manager)
        item_id_str = str(item_id)
        self.set_widget_data(manager, item_id_str)
        if checked != item_id_str:
            await self._process_on_state_changed(event, item_id_str, manager)

    def is_checked(
            self, item_id: T, manager: DialogManager,
    ) -> bool:
        return str(item_id) == self._get_checked(manager)

    def _preview_checked_id(
            self, manager: DialogManager, item_id: str,
    ) -> str:
        return self.get_widget_data(manager, item_id)

    def _is_text_checked(
            self, data: Dict, case: Case, manager: DialogManager,
    ) -> bool:
        item_id = self.item_id_getter(data["item"])
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

    def managed(self, manager: DialogManager) -> "ManagedRadio[T]":
        return ManagedRadio(self, manager)


class ManagedRadio(ManagedWidget[Radio[T]], Generic[T]):
    def get_checked(self) -> Optional[T]:
        """Get an id of selected item."""
        return self.widget.get_checked(self.manager)

    async def set_checked(self, item_id: T) -> None:
        """Get set which item is selected."""
        return await self.widget.set_checked(
            self.manager.event, item_id, self.manager,
        )

    def is_checked(
            self, item_id: T,
    ) -> bool:
        """Get if specified item is checked."""
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
            on_click: Union[
                OnItemClick["ManagedMultiselect[T]", T],
                WidgetEventProcessor, None,
            ] = None,
            on_state_changed: Union[
                OnItemStateChanged["ManagedMultiselect[T]", T],
                WidgetEventProcessor, None,
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
            self, item_id: T, manager: DialogManager,
    ) -> bool:
        data = self._get_checked(manager)
        return str(item_id) in data

    def _get_checked(self, manager: DialogManager) -> List[str]:
        return self.get_widget_data(manager, [])

    def get_checked(self, manager: DialogManager) -> List[T]:
        return [self.type_factory(item) for item in self._get_checked(manager)]

    async def reset_checked(
            self, event: ChatEvent, manager: DialogManager,
    ) -> None:
        self.set_widget_data(manager, [])

    async def set_checked(
            self,
            event: ChatEvent,
            item_id: T,
            checked: bool,
            manager: DialogManager,
    ) -> None:
        item_id_str = str(item_id)
        data: List = self._get_checked(manager)
        changed = False
        if item_id_str in data:
            if not checked:
                if len(data) > self.min_selected:
                    data.remove(item_id_str)
                    changed = True
        else:
            if checked:
                if self.max_selected == 0 or self.max_selected > len(data):
                    data.append(item_id_str)
                    changed = True
        if changed:
            self.set_widget_data(manager, data)
            await self._process_on_state_changed(event, item_id_str, manager)

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

    def managed(self, manager: DialogManager) -> "ManagedMultiselect[T]":
        return ManagedMultiselect(self, manager)


class ManagedMultiselect(ManagedWidget[Multiselect[T]], Generic[T]):
    def is_checked(self, item_id: T) -> bool:
        """Get if an item identified by ``item_id`` is checked."""
        return self.widget.is_checked(item_id, self.manager)

    def get_checked(self) -> List[T]:
        """Get a list of checked items ids."""
        return self.widget.get_checked(self.manager)

    async def reset_checked(self):
        """Reset all items to their default state."""
        return await self.widget.reset_checked(
            self.manager.event, self.manager,
        )

    async def set_checked(self, item_id: T, checked: bool) -> None:
        """Set an item identified by ``item_id`` as checked or unchecked."""
        return await self.widget.set_checked(
            self.manager.event, item_id, checked, self.manager,
        )


class Toggle(Radio[T], Generic[T]):
    def __init__(
            self,
            text: Text,
            id: str,
            item_id_getter: ItemIdGetter,
            items: ItemsGetterVariant,
            type_factory: TypeFactory[T] = str,
            on_click: Union[
                OnItemClick["ManagedToggle[T]", T],
                WidgetEventProcessor, None,
            ] = None,
            on_state_changed: Union[
                OnItemStateChanged["ManagedToggle[T]", T],
                WidgetEventProcessor, None,
            ] = None,
            when: Union[str, Callable] = None,
    ):
        super().__init__(
            checked_text=text, unchecked_text=text,
            id=id, item_id_getter=item_id_getter,
            items=items, type_factory=type_factory, on_click=on_click,
            on_state_changed=on_state_changed, when=when,
        )

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        items_it = iter(self.items_getter(data))
        first_item = next(items_it, None)
        if first_item is None:
            return [[]]

        selected = self.get_checked(manager)
        # by default first one is shown
        if selected is None:
            pos = 0
            item = first_item
        elif self.item_id_getter(first_item) == selected:
            pos = 0
            item = first_item
        else:
            pos, item = next(
                (
                    (n, i)
                    for n, i in enumerate(items_it, 1)
                    if self.item_id_getter(i) == selected
                ),
                (0, first_item),
            )
        # click leads to the next item
        next_item = next(items_it, first_item)
        return [[
            await self._render_button(pos, item, next_item, data, manager),
        ]]


class ManagedToggle(ManagedRadio[Radio[T]], Generic[T]):
    pass
