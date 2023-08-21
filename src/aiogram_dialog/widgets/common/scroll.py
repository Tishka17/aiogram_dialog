from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Dict, Protocol, Union

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor, WidgetEventProcessor,
)
from .action import Actionable
from .managed import ManagedWidget


class Scroll(Widget, Protocol):
    @abstractmethod
    async def get_page_count(self, data: Dict, manager: DialogManager) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_page(self, manager: DialogManager) -> int:
        raise NotImplementedError

    @abstractmethod
    async def set_page(
            self, event: ChatEvent, page: int, manager: DialogManager,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def managed(self, manager: DialogManager) -> "ManagedScroll":
        raise NotImplementedError


class ManagedScroll(ManagedWidget[Scroll]):
    async def get_page_count(self, data: Dict) -> int:
        return await self.widget.get_page_count(data, self.manager)

    async def get_page(self) -> int:
        return await self.widget.get_page(self.manager)

    async def set_page(self, page: int) -> None:
        return await self.widget.set_page(
            self.manager.event, page, self.manager,
        )


OnPageChanged = Callable[
    [ChatEvent, ManagedScroll, DialogManager],
    Awaitable,
]
OnPageChangedVariants = Union[OnPageChanged, WidgetEventProcessor, None]


class BaseScroll(Actionable, Scroll, ABC):
    def __init__(
            self,
            id: str,
            on_page_changed: OnPageChangedVariants = None,
    ):
        super().__init__(id=id)
        self.on_page_changed = ensure_event_processor(on_page_changed)

    async def get_page(self, manager: DialogManager) -> int:
        return self.get_widget_data(manager, 0)

    async def set_page(
            self, event: ChatEvent, page: int, manager: DialogManager,
    ) -> None:
        self.set_widget_data(manager, page)
        await self.on_page_changed.process_event(
            event,
            self.managed(manager),
            manager,
        )

    def managed(self, manager: DialogManager) -> ManagedScroll:
        return ManagedScroll(self, manager)
