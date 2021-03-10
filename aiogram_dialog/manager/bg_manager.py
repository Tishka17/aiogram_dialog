from typing import Any, Dict

from aiogram import Bot
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, CallbackQuery, Chat, User

from .intent import (
    Intent, Data, Action, DialogStartEvent, DialogSwitchEvent, DialogUpdateEvent, ChatEvent
)
from .protocols import DialogRegistryProto, BgManagerProto


def get_chat(event: ChatEvent) -> Chat:
    if isinstance(event, (Message, DialogUpdateEvent)):
        return event.chat
    elif isinstance(event, CallbackQuery):
        return event.message.chat


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
