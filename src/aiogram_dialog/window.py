from logging import getLogger
from typing import Dict, List, Optional

from aiogram.fsm.state import State
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    UNSET_PARSE_MODE,
)

from aiogram_dialog.api.entities import MediaAttachment, NewMessage
from aiogram_dialog.api.internal import Widget, WindowProtocol
from .api.protocols import DialogManager, DialogProtocol
from .widgets.data import PreviewAwareGetter
from .widgets.kbd import Keyboard
from .widgets.utils import (
    ensure_data_getter,
    ensure_widgets,
    GetterVariant,
    WidgetSrc,
)

logger = getLogger(__name__)


class Window(WindowProtocol):
    def __init__(
            self,
            *widgets: WidgetSrc,
            state: State,
            getter: GetterVariant = None,
            parse_mode: Optional[str] = UNSET_PARSE_MODE,
            disable_web_page_preview: Optional[bool] = None,
            preview_add_transitions: Optional[List[Keyboard]] = None,
            preview_data: GetterVariant = None,
    ):
        (
            self.text,
            self.keyboard,
            self.on_message,
            self.media,
        ) = ensure_widgets(widgets)
        self.getter = PreviewAwareGetter(
            ensure_data_getter(getter),
            ensure_data_getter(preview_data),
        )
        self.state = state
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        self.preview_add_transitions = preview_add_transitions

    async def render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        return await self.text.render_text(data, manager)

    async def render_media(
            self, data: Dict, manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        if self.media:
            return await self.media.render_media(data, manager)

    async def render_kbd(
            self, data: Dict, manager: DialogManager,
    ) -> InlineKeyboardMarkup:
        keyboard = await self.keyboard.render_keyboard(data, manager)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def load_data(
            self, dialog: "DialogProtocol",
            manager: DialogManager,
    ) -> Dict:
        data = await dialog.load_data(manager)
        data.update(await self.getter(**manager.middleware_data))
        return data

    async def process_message(
            self, message: Message, dialog: DialogProtocol,
            manager: DialogManager,
    ) -> None:
        if self.on_message:
            await self.on_message.process_message(message, dialog, manager)

    async def process_callback(
            self, callback: CallbackQuery, dialog: DialogProtocol,
            manager: DialogManager,
    ) -> None:
        if self.keyboard:
            await self.keyboard.process_callback(callback, dialog, manager)

    async def render(
            self, dialog: DialogProtocol,
            manager: DialogManager,
    ) -> NewMessage:
        logger.debug("Show window: %s", self)
        chat = manager.middleware_data["event_chat"]
        current_data = await self.load_data(dialog, manager)
        return NewMessage(
            chat=chat,
            text=await self.render_text(current_data, manager),
            reply_markup=await self.render_kbd(current_data, manager),
            parse_mode=self.parse_mode,
            disable_web_page_preview=self.disable_web_page_preview,
            media=await self.render_media(current_data, manager),
        )

    def get_state(self) -> State:
        return self.state

    def find(self, widget_id) -> Optional[Widget]:
        for root in (self.text, self.keyboard, self.on_message):
            if root:
                if found := root.find(widget_id):
                    return found
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}({self.state})>"
