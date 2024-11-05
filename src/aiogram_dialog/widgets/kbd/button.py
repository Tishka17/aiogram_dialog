from collections.abc import Awaitable, Callable
from typing import Optional, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton, WebAppInfo

from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text
from aiogram_dialog.widgets.widget_event import (
    WidgetEventProcessor,
    ensure_event_processor,
)

from .base import Keyboard

OnClick = Callable[[CallbackQuery, "Button", DialogManager], Awaitable]


class Button(Keyboard):
    def __init__(
            self,
            text: Text,
            id: str,
            on_click: Union[OnClick, WidgetEventProcessor, None] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.text = text
        self.on_click = ensure_event_processor(on_click)

    async def _process_own_callback(
            self,
            callback: CallbackQuery,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        await self.on_click.process_event(callback, self, manager)
        return True

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    callback_data=self._own_callback_data(),
                ),
            ],
        ]


class Url(Keyboard):
    def __init__(
            self,
            text: Text,
            url: Text,
            id: Optional[str] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.text = text
        self.url = url

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    url=await self.url.render_text(data, manager),
                ),
            ],
        ]


class WebApp(Url):
    async def _render_keyboard(
            self, data: dict, manager: DialogManager,
    ) -> list[list[InlineKeyboardButton]]:
        text = await self.text.render_text(data, manager)

        web_app_url = await self.url.render_text(data, manager)
        web_app_info = WebAppInfo(url=web_app_url)

        return [[InlineKeyboardButton(text=text, web_app=web_app_info)]]


class SwitchInlineQuery(Keyboard):
    def __init__(
            self,
            text: Text,
            switch_inline_query: Text,
            id: Optional[str] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.text = text
        self.switch_inline = switch_inline_query

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> list[list[InlineKeyboardButton]]:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    switch_inline_query=await self.switch_inline.render_text(
                        data, manager,
                    ),
                ),
            ],
        ]
