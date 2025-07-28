from typing import Optional

from aiogram.types import (
    ChatAdministratorRights,
    KeyboardButton,
    KeyboardButtonPollType,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
)

from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text

from .base import Keyboard


class RequestContact(Keyboard):
    def __init__(
            self,
            text: Text,
            when: WhenCondition = None,
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


class RequestUsers(Keyboard):
    def __init__(
        self,
        text: Text,
        request_id: int,
        max_quantity: int = 1,
        user_is_bot: bool | None = None,
        user_is_premium: bool | None = None,
        request_name: bool = None,
        request_username: bool | None = None,
        request_photo: bool | None = None,
        when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.request = KeyboardButtonRequestUsers(
            request_id=request_id,
            max_quantity=max_quantity,
            user_is_bot=user_is_bot,
            user_is_premium=user_is_premium,
            request_name=request_name,
            request_username=request_username,
            request_photo=request_photo,
        )

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_users=self.request,
                ),
            ],
        ]


class RequestChat(Keyboard):
    def __init__(
            self,
            text: Text,
            request_id: int,
            chat_is_channel: bool = False,
            chat_is_forum: Optional[bool] = None,
            chat_has_username: Optional[bool] = None,
            chat_is_created: Optional[bool] = None,
            user_administrator_rights: Optional[ChatAdministratorRights] = None,
            bot_administrator_rights: Optional[ChatAdministratorRights] = None,
            bot_is_member: Optional[bool] = None,
            request_title: Optional[bool] = None,
            request_username: Optional[bool] = None,
            request_photo: Optional[bool] = None,
            when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.request = KeyboardButtonRequestChat(
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

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_chat=self.request,
                ),
            ],
        ]


class RequestLocation(Keyboard):
    def __init__(
            self,
            text: Text,
            when: WhenCondition = None,
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


class RequestPoll(Keyboard):
    def __init__(
            self,
            text: Text,
            poll_type: Optional[str] = None,
            when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.poll_type = poll_type

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        text = await self.text.render_text(data, manager)
        request_poll = KeyboardButtonPollType(type=self.poll_type)

        return [
            [
                KeyboardButton(
                    text=text,
                    request_poll=request_poll,
                ),
            ],
        ]
