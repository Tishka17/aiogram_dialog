from collections.abc import Callable
from typing import Optional, Union

from aiogram.types import (
    ChatAdministratorRights,
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUser,
    KeyboardButtonRequestUsers,
)

from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.text import Text

from .base import Keyboard


class RequestContact(Keyboard):
    def __init__(
        self,
        text: Text,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_contact=True,
                ),
            ],
        ]


class RequestLocation(Keyboard):
    def __init__(
        self,
        text: Text,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_location=True,
                ),
            ],
        ]


class RequestChat(Keyboard):
    def __init__(
        self,
        text: Text,
        request_id: int,
        chat_is_channel: bool,
        chat_is_forum: Optional[bool] = None,
        chat_has_username: Optional[bool] = None,
        chat_is_created: Optional[bool] = None,
        user_administrator_rights: Optional[ChatAdministratorRights] = None,
        bot_administrator_rights: Optional[ChatAdministratorRights] = None,
        bot_is_member: Optional[bool] = None,
        request_title: Optional[bool] = None,
        request_username: Optional[bool] = None,
        request_photo: Optional[bool] = None,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.request_id = request_id
        self.chat_is_channel = chat_is_channel
        self.chat_is_forum = chat_is_forum
        self.chat_has_username = chat_has_username
        self.chat_is_created = chat_is_created
        self.user_administrator_rights = user_administrator_rights
        self.bot_administrator_rights = bot_administrator_rights
        self.bot_is_member = bot_is_member
        self.request_title = request_title
        self.request_username = request_username
        self.request_photo = request_photo

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_chat=KeyboardButtonRequestChat(
                        request_id=self.request_id,
                        chat_is_channel=self.chat_is_channel,
                        chat_is_forum=self.chat_is_forum,
                        chat_has_username=self.chat_has_username,
                        chat_is_created=self.chat_is_created,
                        user_administrator_rights=self.user_administrator_rights,
                        bot_administrator_rights=self.bot_administrator_rights,
                        bot_is_member=self.bot_is_member,
                        request_title=self.request_title,
                        request_username=self.request_username,
                        request_photo=self.request_photo,
                    ),
                ),
            ],
        ]


class RequestUser(Keyboard):
    def __init__(
        self,
        text: Text,
        request_id: int,
        user_is_bot: Optional[bool] = None,
        user_is_premium: Optional[bool] = None,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.request_id = request_id
        self.user_is_bot = user_is_bot
        self.user_is_premium = user_is_premium

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_user=KeyboardButtonRequestUser(
                        request_id=self.request_id,
                        user_is_bot=self.user_is_bot,
                        user_is_premium=self.user_is_premium,
                    ),
                ),
            ],
        ]


class RequestUsers(Keyboard):
    def __init__(
        self,
        text: Text,
        request_id: int,
        user_is_bot: Optional[bool] = None,
        user_is_premium: Optional[bool] = None,
        max_quantity: Optional[int] = None,
        request_name: Optional[bool] = None,
        request_username: Optional[bool] = None,
        request_photo: Optional[bool] = None,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.request_id = request_id
        self.user_is_bot = user_is_bot
        self.user_is_premium = user_is_premium
        self.max_quantity = max_quantity
        self.request_name = request_name
        self.request_username = request_username
        self.request_photo = request_photo

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_users=KeyboardButtonRequestUsers(
                        request_id=self.request_id,
                        user_is_bot=self.user_is_bot,
                        user_is_premium=self.user_is_premium,
                        max_quantity=self.max_quantity,
                        request_name=self.request_name,
                        request_username=self.request_username,
                        request_photo=self.request_photo,
                    ),
                ),
            ],
        ]
