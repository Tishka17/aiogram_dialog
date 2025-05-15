import warnings
from logging import getLogger
from typing import Any, Optional, cast

from aiogram.fsm.state import State
from aiogram.types import UNSET_PARSE_MODE, CallbackQuery, LinkPreviewOptions, Message

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
from .widgets.link_preview import LinkPreview
from .widgets.markup.inline_keyboard import InlineKeyboardFactory
from .widgets.utils import GetterVariant, WidgetSrc, ensure_data_getter, ensure_widgets

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
        disable_web_page_preview: Optional[bool] = None,
        preview_add_transitions: Optional[list[Keyboard]] = None,
        preview_data: GetterVariant = None,
        slots: Optional[list[list[WidgetSrc]]] = None,
    ):
        (
            self.text,
            self.keyboard,
            self.on_message,
            self.media,
            self.link_preview,
        ) = ensure_widgets(widgets)
        self.getter = PreviewAwareGetter(
            ensure_data_getter(getter),
            ensure_data_getter(preview_data),
        )
        self.state = state
        self.on_process_result = on_process_result
        self.markup_factory = markup_factory
        self.parse_mode = parse_mode
        self.preview_add_transitions = preview_add_transitions
        self.disable_web_page_preview = disable_web_page_preview

        if disable_web_page_preview is True:
            if self.link_preview:
                raise ValueError(
                    "Cannot use LinkPreview widget for the primary message "
                    "together with disable_web_page_preview=True.",
                )
            warnings.warn(
                "`disable_web_page_preview=True` on Window is deprecated, "
                "pass a `LinkPreview(is_disabled=True)` widget directly instead.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            self.link_preview = LinkPreview(is_disabled=True)
        elif disable_web_page_preview is False:
            warnings.warn(
                "`disable_web_page_preview=False` on Window is deprecated and has no effect "
                "if no LinkPreview widget is present. Link previews are enabled by default. "
                "To configure, pass a `LinkPreview` widget.",
                category=DeprecationWarning,
                stacklevel=2,
            )

        self.slot_definitions = []
        if slots:
            for slot_widget_sources in slots:
                s_text, s_kbd, s_on_msg, s_media, s_link_prev = ensure_widgets(
                    slot_widget_sources,
                )
                self.slot_definitions.append(
                    {
                        "text": s_text,
                        "keyboard": s_kbd,
                        "on_message": s_on_msg,
                        "media": s_media,
                        "link_preview": s_link_prev,
                    },
                )

    async def _render_single_message_content(
        self,
        text_widget,
        media_widget,
        kbd_widget,
        link_preview_widget,
        data: dict,
        manager: DialogManager,
    ) -> tuple[
        str,
        Optional[MediaAttachment],
        MarkupVariant,
        Optional[LinkPreviewOptions],
    ]:
        text_content = await text_widget.render_text(data, manager)

        media_content = None
        if media_widget:
            media_content = await media_widget.render_media(data, manager)

        keyboard_markup_buttons = []
        if kbd_widget:
            keyboard_markup_buttons = await kbd_widget.render_keyboard(data, manager)

        reply_markup_content = await self.markup_factory.render_markup(
            data,
            manager,
            keyboard_markup_buttons,
        )

        link_preview_options_content = None
        if link_preview_widget:
            link_preview_options_content = (
                await link_preview_widget.render_link_preview(
                    data,
                    manager,
                )
            )

        return (
            text_content,
            media_content,
            reply_markup_content,
            link_preview_options_content,
        )

    async def render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        return await self.text.render_text(data, manager)

    async def render_media(
        self,
        data: dict,
        manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        if self.media:
            return await self.media.render_media(data, manager)
        return None

    async def render_kbd(
        self,
        data: dict,
        manager: DialogManager,
    ) -> MarkupVariant:
        keyboard = await self.keyboard.render_keyboard(data, manager)
        return await self.markup_factory.render_markup(
            data,
            manager,
            keyboard,
        )

    async def render_link_preview(
        self,
        data: dict,
        manager: DialogManager,
    ) -> Optional[LinkPreviewOptions]:
        if self.link_preview:
            return await self.link_preview.render_link_preview(data, manager)
        return None

    async def load_data(
        self,
        dialog: "DialogProtocol",
        manager: DialogManager,
    ) -> dict:
        data = await dialog.load_data(manager)
        middleware_data_for_getter = manager.middleware_data.copy()
        middleware_data_for_getter.pop("dialog_manager", None)
        data.update(await self.getter(manager, **middleware_data_for_getter))
        return data

    async def process_message(
        self,
        message: Message,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        if self.on_message:
            return await self.on_message.process_message(
                message,
                dialog,
                manager,
            )
        return False

    async def process_callback(
        self,
        callback: CallbackQuery,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        if self.keyboard:
            if await self.keyboard.process_callback(
                callback,
                dialog,
                manager,
            ):
                return True

        for slot_def in self.slot_definitions:
            s_kbd_widget = slot_def["keyboard"]
            if s_kbd_widget:
                if await s_kbd_widget.process_callback(callback, dialog, manager):
                    return True
        return False

    async def process_result(
        self,
        start_data: Data,
        result: Any,
        manager: DialogManager,
    ) -> None:
        if self.on_process_result:
            await self.on_process_result(start_data, result, manager)

    async def render(
        self,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> list[NewMessage]:
        logger.debug("Show window: %s", self)
        chat = manager.middleware_data["event_chat"]
        event_context = cast(
            "EventContext",
            manager.middleware_data.get(EVENT_CONTEXT_KEY),
        )

        messages_to_send: list[NewMessage] = []

        try:
            current_data = await self.load_data(dialog, manager)
        except Exception:
            logger.error("Cannot get window data for state %s", self.state)
            raise

        try:
            # Primary message content
            text, media, reply_markup, link_preview_options_from_widget = (
                await self._render_single_message_content(
                    self.text,
                    self.media,
                    self.keyboard,
                    self.link_preview,
                    current_data,
                    manager,
                )
            )

            link_preview_options_for_primary: Optional[LinkPreviewOptions] = None
            if link_preview_options_from_widget:
                link_preview_options_for_primary = link_preview_options_from_widget
            elif self.disable_web_page_preview is True:
                link_preview_options_for_primary = LinkPreviewOptions(is_disabled=True)

            message = NewMessage(
                chat=chat,
                thread_id=event_context.thread_id,
                business_connection_id=event_context.business_connection_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=self.parse_mode,
                media=media,
                link_preview_options=link_preview_options_for_primary,
            )
            messages_to_send.append(message)

            for slot_def in self.slot_definitions:
                s_text_widget = slot_def["text"]
                s_media_widget = slot_def["media"]
                s_kbd_widget = slot_def["keyboard"]
                s_link_prev_widget = slot_def["link_preview"]

                s_text, s_media, s_reply_markup, s_link_preview_options_from_widget = (
                    await self._render_single_message_content(
                        s_text_widget,
                        s_media_widget,
                        s_kbd_widget,
                        s_link_prev_widget,
                        current_data,
                        manager,
                    )
                )

                link_preview_options_for_slot: Optional[LinkPreviewOptions] = None
                if s_link_preview_options_from_widget:
                    link_preview_options_for_slot = s_link_preview_options_from_widget
                elif (
                    self.disable_web_page_preview is True
                ):  # Window-level flag as fallback
                    link_preview_options_for_slot = LinkPreviewOptions(is_disabled=True)

                slot_message = NewMessage(
                    chat=chat,
                    thread_id=event_context.thread_id,
                    business_connection_id=event_context.business_connection_id,
                    text=s_text,
                    reply_markup=s_reply_markup,
                    parse_mode=self.parse_mode,
                    media=s_media,
                    link_preview_options=link_preview_options_for_slot,
                )
                messages_to_send.append(slot_message)
        except Exception:
            logger.error("Cannot render window for state %s", self.state)
            raise

        return messages_to_send

    def get_state(self) -> State:
        return self.state

    def find(self, widget_id) -> Optional[Widget]:
        for root in (
            self.text,
            self.keyboard,
            self.on_message,
            self.media,
            self.link_preview,
        ):
            if root and (found := root.find(widget_id)):
                return found

        for slot_def in self.slot_definitions:
            for widget_key in [
                "text",
                "keyboard",
                "on_message",
                "media",
                "link_preview",
            ]:
                widget = slot_def[widget_key]
                if widget and (found := widget.find(widget_id)):
                    return found
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}({self.state})>"
