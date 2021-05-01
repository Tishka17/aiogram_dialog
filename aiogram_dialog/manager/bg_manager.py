from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.dispatcher.filters.state import State
from aiogram.types import Chat, User

from .intent import (
    Intent, Data, Action, DialogStartEvent, DialogSwitchEvent, DialogUpdateEvent
)
from .protocols import DialogRegistryProto, BgManagerProto


class BgManager(BgManagerProto):
    def __init__(
            self,
            user: User,
            chat: Chat,
            bot: Bot,
            registry: DialogRegistryProto,
            intent: Intent,
            current_state: State
    ):
        self.user = user
        self.chat = chat
        self.bot = bot
        self.registry = registry
        self.intent = intent
        self.current_state = current_state

    def current_intent(self) -> Intent:
        return self.intent

    def bg(self, user_id: Optional[int] = None, chat_id: Optional[int] = None) -> BgManagerProto:
        if user_id is not None:
            user = User(id=user_id)
        else:
            user = self.user
        if chat_id is not None:
            chat = Chat(id=chat_id)
        else:
            chat = self.chat

        return BgManager(
            user,
            chat,
            self.bot,
            self.registry,
            self.current_intent(),
            self.current_state,
        )

    async def done(self, result: Any = None):
        await self.registry.notify(DialogUpdateEvent(
            self.bot,
            self.user,
            self.chat,
            Action.DONE,
            result,
        ))

    async def start(self, state: State, data: Data = None, reset_stack: bool = False):
        await self.registry.notify(DialogStartEvent(
            self.bot,
            self.user,
            self.chat,
            Action.START,
            data,
            state,
            reset_stack,
        ))

    async def switch_to(self, state: State):
        await self.registry.notify(DialogSwitchEvent(
            self.bot,
            self.user,
            self.chat,
            Action.SWITCH,
            {},
            state,
        ))

    async def update(self, data: Dict):
        await self.registry.notify(DialogUpdateEvent(
            self.bot,
            self.user,
            self.chat,
            Action.UPDATE,
            data,
        ))
