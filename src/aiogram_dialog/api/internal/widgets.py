from typing import (
    Any, Awaitable, Callable, Dict, List, Optional, Protocol,
    runtime_checkable,
)

from aiogram.types import CallbackQuery, InlineKeyboardButton, Message

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.api.protocols import DialogProtocol


@runtime_checkable
class Widget(Protocol):
    def managed(self, manager: DialogManager) -> Any:
        raise NotImplementedError

    def find(self, widget_id: str) -> Optional["Widget"]:
        raise NotImplementedError


@runtime_checkable
class TextWidget(Widget, Protocol):
    async def render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        """Create text."""
        raise NotImplementedError


@runtime_checkable
class KeyboardWidget(Widget, Protocol):
    async def render_keyboard(
            self, data: Dict, manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        """Create Inline keyboard contents."""
        raise NotImplementedError

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
    async def render_media(
            self, data: Any, manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        """Create media attachment."""
        raise NotImplementedError


@runtime_checkable
class InputWidget(Widget, Protocol):
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
