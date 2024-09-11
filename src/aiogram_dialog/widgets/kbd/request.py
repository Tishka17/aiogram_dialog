from typing import Callable, Dict, Union

from aiogram.types import (
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
        data: Dict,
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
        data: Dict,
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
        RequestButton: KeyboardButtonRequestChat,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.RequestButton = RequestButton

    async def _render_keyboard(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_chat=self.RequestButton,
                ),
            ],
        ]


class RequestUser(Keyboard):
    def __init__(
        self,
        text: Text,
        RequestButton: KeyboardButtonRequestUser,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.RequestButton = RequestButton

    async def _render_keyboard(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_user=self.RequestButton,
                ),
            ],
        ]


class RequestUsers(Keyboard):
    def __init__(
        self,
        text: Text,
        RequestButton: KeyboardButtonRequestUsers,
        when: Union[str, Callable, None] = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.RequestButton = RequestButton

    async def _render_keyboard(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_users=self.RequestButton,
                ),
            ],
        ]
