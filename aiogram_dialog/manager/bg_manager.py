from typing import Any, Dict

from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, CallbackQuery, Chat

from .intent import Intent, Data, DialogUpdateEvent, Action, DialogStartEvent, DialogSwitchEvent, ChatEvent
from .protocols import DialogRegistryProto, ManagedDialogProto, DialogManagerProto


def chat(event: ChatEvent) -> Chat:
    if isinstance(event, (Message, DialogUpdateEvent)):
        return event.chat
    elif isinstance(event, CallbackQuery):
        return event.message.chat


class BgManager(DialogManagerProto):
    def __init__(
            self, event: ChatEvent, registry: DialogRegistryProto, intent: Intent, dialog: ManagedDialogProto
    ):
        self.event = event
        self.registry = registry
        self.intent = intent
        self._dialog = dialog

    def dialog(self):
        return self._dialog

    def current_intent(self) -> Intent:
        return self.intent

    async def close(self):
        raise NotImplementedError("Cannot silently close from background context. Use `done` method")

    async def done(self, result: Any = None):
        await self.registry.notify(DialogUpdateEvent(
            self.event.bot,
            self.event.from_user,
            chat(self.event),
            getattr(self.event, "message", None),
            Action.DONE,
            self.intent,
            result,
        ))

    async def start(self, state: State, data: Data = None, reset_stack: bool = False):
        await self.registry.notify(DialogStartEvent(
            self.event.bot,
            self.event.from_user,
            chat(self.event),
            getattr(self.event, "message", None),
            Action.START,
            self.intent,
            data,
            state,
            reset_stack,
        ))

    async def switch_to(self, state):
        await self.registry.notify(DialogSwitchEvent(
            self.event.bot,
            self.event.from_user,
            chat(self.event),
            getattr(self.event, "message", None),
            Action.SWITCH,
            self.intent,
            {},
            state,
        ))

    async def update(self, data: Dict):
        await self.registry.notify(DialogUpdateEvent(
            self.event.bot,
            self.event.from_user,
            chat(self.event),
            getattr(self.event, "message", None),
            Action.UPDATE,
            self.intent,
            data,
        ))
