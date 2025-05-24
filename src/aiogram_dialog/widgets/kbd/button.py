from collections.abc import Awaitable, Callable
from typing import Optional, Union

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    LoginUrl,
    SwitchInlineQueryChosenChat,
    WebAppInfo,
)

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


class LoginURLButton(Keyboard):
    def __init__(
            self,
            text: Text,
            url: Text,
            forward_text: Optional[Text] = None,
            bot_username: Optional[Text] = None,
            request_write_access: Optional[bool] = None,
            id: Optional[str] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.text = text
        self.url = url
        self.forward_text = forward_text
        self.bot_username = bot_username
        self.request_write_access = request_write_access

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        text = await self.text.render_text(data, manager)
        url = await self.url.render_text(data, manager)

        forward_text = None
        if self.forward_text:
            forward_text = await self.forward_text.render_text(data, manager)

        bot_username = None
        if self.bot_username:
            bot_username = await self.bot_username.render_text(data, manager)

        login_url = LoginUrl(
            url=url,
            forward_text=forward_text,
            bot_username=bot_username,
            request_write_access=self.request_write_access,
        )

        return [
            [
                InlineKeyboardButton(
                    text=text,
                    login_url=login_url,
                ),
            ],
        ]


class SwitchInlineQueryCurrentChat(Keyboard):
    def __init__(
            self,
            text: Text,
            switch_inline_query_current_chat: Text,
            id: Optional[str] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.text = text
        self.switch_inline_query_current_chat = (
            switch_inline_query_current_chat
        )

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        text = await self.text.render_text(data, manager)
        query = await self.switch_inline_query_current_chat.render_text(
            data, manager,
        )

        return [
            [
                InlineKeyboardButton(
                    text=text,
                    switch_inline_query_current_chat=query,
                ),
            ],
        ]


class SwitchInlineQueryChosenChatButton(Keyboard):
    def __init__(
            self,
            text: Text,
            query: Text,
            allow_user_chats: Optional[bool] = None,
            allow_bot_chats: Optional[bool] = None,
            allow_group_chats: Optional[bool] = None,
            allow_channel_chats: Optional[bool] = None,
            id: Optional[str] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.text = text
        self.query = query
        self.allow_user_chats = allow_user_chats
        self.allow_bot_chats = allow_bot_chats
        self.allow_group_chats = allow_group_chats
        self.allow_channel_chats = allow_channel_chats

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        text = await self.text.render_text(data, manager)
        query = await self.query.render_text(data, manager)

        switch_inline_query_chosen_chat = SwitchInlineQueryChosenChat(
            query=query,
            allow_user_chats=self.allow_user_chats,
            allow_bot_chats=self.allow_bot_chats,
            allow_group_chats=self.allow_group_chats,
            allow_channel_chats=self.allow_channel_chats,
        )

        return [
            [
                InlineKeyboardButton(
                    text=text,
                    switch_inline_query_chosen_chat=switch_inline_query_chosen_chat,
                ),
            ],
        ]
