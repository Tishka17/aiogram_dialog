from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.dispatcher.filters.state import State
from aiogram.types import Chat, User

from .protocols import DialogRegistryProto, BaseDialogManager
from ..context.events import (
    Data, Action, DialogStartEvent, DialogSwitchEvent, DialogUpdateEvent, StartMode
)
from ..context.stack import DEFAULT_STACK_ID


class BgManager(BaseDialogManager):
    def __init__(
            self,
            user: User,
            chat: Chat,
            bot: Bot,
            registry: DialogRegistryProto,
            intent_id: Optional[str],
            stack_id: Optional[str],
    ):
        self.user = user
        self.chat = chat
        self.bot = bot
        self._registry = registry
        self.intent_id = intent_id
        self.stack_id = stack_id

    @property
    def registry(self) -> DialogRegistryProto:
        return self._registry

    def bg(
            self,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            stack_id: Optional[str] = None,
    ) -> "BaseDialogManager":
        if user_id is not None:
            user = User(id=user_id)
        else:
            user = self.user
        if chat_id is not None:
            chat = Chat(id=chat_id)
        else:
            chat = self.chat

        same_chat = (user.id == self.user.id and chat.id == self.chat.id)
        if stack_id is None:
            if same_chat:
                stack_id = self.stack_id
                intent_id = self.intent_id
            else:
                stack_id = DEFAULT_STACK_ID
                intent_id = None
        else:
            intent_id = None

        return BgManager(
            user=user,
            chat=chat,
            bot=self.bot,
            registry=self.registry,
            intent_id=intent_id,
            stack_id=stack_id,
        )

    def _base_event_params(self):
        return {
            "bot": self.bot,
            "from_user": self.user,
            "chat": self.chat,
            "intent_id": self.intent_id,
            "stack_id": self.stack_id,
        }

    async def done(self, result: Any = None) -> None:
        await self.registry.notify(DialogUpdateEvent(
            action=Action.DONE,
            data=result,
            **self._base_event_params()
        ))

    async def start(self, state: State, data: Data = None,
                    mode: StartMode = StartMode.NORMAL) -> None:
        await self.registry.notify(DialogStartEvent(
            action=Action.START,
            data=data,
            new_state=state,
            mode=mode,
            **self._base_event_params()
        ))

    async def switch_to(self, state: State) -> None:
        await self.registry.notify(DialogSwitchEvent(
            action=Action.SWITCH,
            data={},
            new_state=state,
            **self._base_event_params()
        ))

    async def update(self, data: Dict) -> None:
        await self.registry.notify(DialogUpdateEvent(
            action=Action.UPDATE,
            data=data,
            **self._base_event_params()
        ))
