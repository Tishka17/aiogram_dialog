from abc import abstractmethod
from typing import (
    Any, Awaitable, Callable, Dict, List, Optional, Protocol,
    runtime_checkable, Union,
)

from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, KeyboardButton, Message,
)

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MarkupVariant, MediaAttachment
from aiogram_dialog.api.protocols import DialogProtocol


@runtime_checkable
class Widget(Protocol):
    @abstractmethod
    def managed(self, manager: DialogManager) -> Any:
        raise NotImplementedError

    @abstractmethod
    def find(self, widget_id: str) -> Optional["Widget"]:
        raise NotImplementedError


@runtime_checkable
class TextWidget(Widget, Protocol):
    @abstractmethod
    async def render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        """Create text."""
        raise NotImplementedError


ButtonVariant = Union[InlineKeyboardButton, KeyboardButton]
RawKeyboard = List[List[ButtonVariant]]


@runtime_checkable
class KeyboardWidget(Widget, Protocol):
    @abstractmethod
    async def render_keyboard(
            self, data: Dict, manager: DialogManager,
    ) -> RawKeyboard:
        """Create Inline keyboard contents."""
        raise NotImplementedError

    @abstractmethod
    async def process_callback(
            self, callback: CallbackQuery, dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        """
        Handle user click on some inline button.

        Invoked regardless if callback belongs to current widget.

        returns True if callback processed and should not be propagated
        """
        raise NotImplementedError


@runtime_checkable
class MediaWidget(Widget, Protocol):
    @abstractmethod
    async def render_media(
            self, data: dict, manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        """Create media attachment."""
        raise NotImplementedError


@runtime_checkable
class InputWidget(Widget, Protocol):
    @abstractmethod
    async def process_message(
            self, message: Message, dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        """
        Handle incoming message from user.

        Invoked regardless if callback belongs to current widget.

        returns True if callback processed and should not be propagated
        """
        raise NotImplementedError


DataGetter = Callable[..., Awaitable[Dict]]


@runtime_checkable
class MarkupFactory(Protocol):
    @abstractmethod
    async def render_markup(
            self, data: dict, manager: DialogManager, keyboard: RawKeyboard,
    ) -> MarkupVariant:
        """Render reply_markup using prepared keyboard."""
        raise NotImplementedError
