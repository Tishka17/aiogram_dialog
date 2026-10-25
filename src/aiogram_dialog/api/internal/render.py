from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from aiogram.types import InputRichMessageMedia, InputRichBlockUnion

from aiogram_dialog.api.entities import (
    ChatEvent,
    Data,
    ShowMode,
)
from aiogram_dialog.api.protocols.manager import DialogManager


class CallbackProcessor(Protocol):
    @abstractmethod
    def callback_data(self, widget_id: str, data: str | None) -> None:
        raise NotImplementedError


class RenderMode(Enum):
    RICH_HTML = "rich_html"
    RICH_MD = "rich_md"
    RICH_BLOCKS = "rich_blocks"


class RenderingContext(Protocol):
    @property
    @abstractmethod
    def callback_processor(self) -> CallbackProcessor:
        raise NotImplementedError

    @property
    @abstractmethod
    def event(self) -> ChatEvent:
        raise NotImplementedError

    @property
    @abstractmethod
    def middleware_data(self) -> dict:
        """Middleware data."""
        raise NotImplementedError

    @property
    @abstractmethod
    def dialog_data(self) -> dict:
        """Dialog data for current context."""
        raise NotImplementedError

    @property
    @abstractmethod
    def start_data(self) -> Data:
        """Start data for current context."""
        raise NotImplementedError

    @property
    @abstractmethod
    def show_mode(self) -> ShowMode:
        """Get current show mode, used for next show action."""
        raise NotImplementedError

    @abstractmethod
    def is_preview(self) -> bool:
        """Check if this manager is used only to generate dialog preview."""
        raise NotImplementedError


@dataclass(slots=True)
class RichContent:
    plain: str = ""
    blocks: list[InputRichBlockUnion] = field(default_factory=list)
    media: list[InputRichMessageMedia] = field(default_factory=list)

    def __add__(self, other: RichContent) -> RichContent:
        return RichContent(
            plain=self.plain + other.plain,
            blocks=self.blocks + other.blocks,
            media=self.media + other.media,
        )


class RichWidget(Protocol):
    @abstractmethod
    async def render_rich(self, data: dict[str, Any], context: RenderingContext, mode: RenderMode) -> RichContent:
        raise NotImplementedError

    @abstractmethod
    def supported_events(self) -> list[object]:  # TODO: specify event types: callback, message, whatever
        raise NotImplementedError

    @abstractmethod
    async def handle_event(self, event: object, dialog_manager: DialogManager) -> None:  # TODO: specify event object
        raise NotImplementedError
