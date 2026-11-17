from collections.abc import Callable

from aiogram.types import (
    ChatAdministratorRights,
    KeyboardButton,
    KeyboardButtonPollType,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
)

from aiogram_dialog.api.internal import RawKeyboard, StyleWidget, TextWidget
from aiogram_dialog.api.internal.widgets import ButtonStyle
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.style import EMPTY_STYLE
from .base import Keyboard


class RequestContact(Keyboard):
    def __init__(
            self,
            text: TextWidget,
            when: str | Callable | None = None,
            style: StyleWidget = EMPTY_STYLE,
    ):
        super().__init__(when=when)
        self.text = text
        self.style = style

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        style = await self.style.render_style(data, manager)
        icon_custom_emoji_id = await self.style.render_emoji(data, manager)

        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_contact=True,
                    style=style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                ),
            ],
        ]


class RequestLocation(Keyboard):
    def __init__(
            self,
            text: TextWidget,
            when: str | Callable | None = None,
            style: StyleWidget = EMPTY_STYLE,
    ):
        super().__init__(when=when)
        self.text = text
        self.style = style

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        style = await self.style.render_style(data, manager)
        icon_custom_emoji_id = await self.style.render_emoji(data, manager)

        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_location=True,
                    style=style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                ),
            ],
        ]


class RequestPoll(Keyboard):
    def __init__(
            self,
            text: TextWidget,
            poll_type: str | None = None,
            when: str | Callable | None = None,
            style: StyleWidget = EMPTY_STYLE,
    ):
        super().__init__(when=when)
        self.text = text
        self.poll_type = poll_type
        self.style = style

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        text = await self.text.render_text(data, manager)
        request_poll = KeyboardButtonPollType(type=self.poll_type)
        style = await self.style.render_style(data, manager)
        icon_custom_emoji_id = await self.style.render_emoji(data, manager)

        return [
            [
                KeyboardButton(
                    text=text,
                    request_poll=request_poll,
                    style=style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                ),
            ],
        ]



class _RequestButton(Keyboard):
    """Reply keyboard button which asks user to choose something."""

    def __init__(
            self,
            text: TextWidget,
            when: str | Callable | None = None,
            style: StyleWidget = EMPTY_STYLE,
    ):
        super().__init__(when=when)
        self.text = text
        self.style = style

    def _button(
            self,
            text: str,
            style: ButtonStyle | None,
            icon_custom_emoji_id: str | None,
    ) -> KeyboardButton:
        raise NotImplementedError

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        style = await self.style.render_style(data, manager)
        icon_custom_emoji_id = await self.style.render_emoji(data, manager)

        return [
            [
                self._button(
                    text=await self.text.render_text(data, manager),
                    style=style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                ),
            ],
        ]


class RequestUsers(_RequestButton):
    def __init__(
            self,
            text: TextWidget,
            request_id: int,
            user_is_bot: bool | None = None,
            user_is_premium: bool | None = None,
            max_quantity: int | None = None,
            request_name: bool | None = None,
            request_username: bool | None = None,
            request_photo: bool | None = None,
            when: str | Callable | None = None,
            style: StyleWidget = EMPTY_STYLE,
    ):
        super().__init__(text=text, when=when, style=style)
        # does not depend on data or manager, so it is built only once
        self.request_users = KeyboardButtonRequestUsers(
            request_id=request_id,
            user_is_bot=user_is_bot,
            user_is_premium=user_is_premium,
            max_quantity=max_quantity,
            request_name=request_name,
            request_username=request_username,
            request_photo=request_photo,
        )

    def _button(self, text, style, icon_custom_emoji_id) -> KeyboardButton:
        return KeyboardButton(
            text=text,
            request_users=self.request_users,
            style=style,
            icon_custom_emoji_id=icon_custom_emoji_id,
        )


class RequestChat(_RequestButton):
    def __init__(
            self,
            text: TextWidget,
            request_id: int,
            chat_is_channel: bool,
            chat_is_forum: bool | None = None,
            chat_has_username: bool | None = None,
            chat_is_created: bool | None = None,
            user_administrator_rights: ChatAdministratorRights | None = None,
            bot_administrator_rights: ChatAdministratorRights | None = None,
            bot_is_member: bool | None = None,
            request_title: bool | None = None,
            request_username: bool | None = None,
            request_photo: bool | None = None,
            when: str | Callable | None = None,
            style: StyleWidget = EMPTY_STYLE,
    ):
        super().__init__(text=text, when=when, style=style)
        # does not depend on data or manager, so it is built only once
        self.request_chat = KeyboardButtonRequestChat(
            request_id=request_id,
            chat_is_channel=chat_is_channel,
            chat_is_forum=chat_is_forum,
            chat_has_username=chat_has_username,
            chat_is_created=chat_is_created,
            user_administrator_rights=user_administrator_rights,
            bot_administrator_rights=bot_administrator_rights,
            bot_is_member=bot_is_member,
            request_title=request_title,
            request_username=request_username,
            request_photo=request_photo,
        )

    def _button(self, text, style, icon_custom_emoji_id) -> KeyboardButton:
        return KeyboardButton(
            text=text,
            request_chat=self.request_chat,
            style=style,
            icon_custom_emoji_id=icon_custom_emoji_id,
        )
