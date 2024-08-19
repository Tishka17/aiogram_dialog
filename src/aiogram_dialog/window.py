from logging import getLogger
from typing import Any, cast, Dict, List, Optional

from aiogram.fsm.state import State
from aiogram.types import (
    CallbackQuery,
    Message,
    UNSET_PARSE_MODE,
)
from aiogram.types.base import UNSET_DISABLE_WEB_PAGE_PREVIEW

from aiogram_dialog.api.entities import (
    EVENT_CONTEXT_KEY,
    EventContext,
    MarkupVariant,
    MediaAttachment,
    NewMessage,
)
from aiogram_dialog.api.internal import Widget, WindowProtocol
from .api.entities import Data
from .api.internal.widgets import MarkupFactory
from .api.protocols import DialogManager, DialogProtocol
from .dialog import OnResultEvent
from .widgets.data import PreviewAwareGetter
from .widgets.kbd import Keyboard
from .widgets.markup.inline_keyboard import InlineKeyboardFactory
from .widgets.utils import (
    ensure_data_getter,
    ensure_widgets,
    GetterVariant,
    WidgetSrc,
)

logger = getLogger(__name__)

_DEFAULT_MARKUP_FACTORY = InlineKeyboardFactory()


class Window(WindowProtocol):
    def __init__(
            self,
            *widgets: WidgetSrc,
            state: State,
            getter: GetterVariant = None,
            on_process_result: Optional[OnResultEvent] = None,
            markup_factory: MarkupFactory = _DEFAULT_MARKUP_FACTORY,
            parse_mode: Optional[str] = UNSET_PARSE_MODE,
            disable_web_page_preview: Optional[bool] = UNSET_DISABLE_WEB_PAGE_PREVIEW,  # noqa: E501
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
        self.on_process_result = on_process_result
        self.markup_factory = markup_factory
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
    ) -> MarkupVariant:
        keyboard = await self.keyboard.render_keyboard(data, manager)
        return await self.markup_factory.render_markup(
            data, manager, keyboard,
        )

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
    ) -> bool:
        if self.on_message:
            return await self.on_message.process_message(
                message, dialog, manager,
            )
        return False

    async def process_callback(
            self, callback: CallbackQuery, dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        if self.keyboard:
            return await self.keyboard.process_callback(
                callback, dialog, manager,
            )
        return False

    async def process_result(
            self, start_data: Data, result: Any, manager: DialogManager,
    ) -> None:
        if self.on_process_result:
            await self.on_process_result(start_data, result, manager)

    async def render(
            self, dialog: DialogProtocol,
            manager: DialogManager,
    ) -> NewMessage:
        logger.debug("Show window: %s", self)
        chat = manager.middleware_data["event_chat"]
        try:
            current_data = await self.load_data(dialog, manager)
        except Exception:  # noqa: B902
            logger.error("Cannot get window data for state %s", self.state)
            raise
        try:
            event_context = cast(
                EventContext, manager.middleware_data.get(EVENT_CONTEXT_KEY),
            )
            return NewMessage(
                chat=chat,
                thread_id=event_context.thread_id,
                business_connection_id=event_context.business_connection_id,
                text=await self.render_text(current_data, manager),
                reply_markup=await self.render_kbd(current_data, manager),
                parse_mode=self.parse_mode,
                disable_web_page_preview=self.disable_web_page_preview,
                media=await self.render_media(current_data, manager),
            )
        except Exception:  # noqa: B902
            logger.error("Cannot render window for state %s", self.state)
            raise

    def get_state(self) -> State:
        return self.state

    def find(self, widget_id) -> Optional[Widget]:
        for root in (self.text, self.keyboard, self.on_message, self.media):
            if root:
                if found := root.find(widget_id):
                    return found
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}({self.state})>"
