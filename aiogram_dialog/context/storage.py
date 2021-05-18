from copy import copy
from typing import Dict, Type, Optional

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import BaseStorage

from .intent import Intent
from .stack import Stack, DEFAULT_STACK_ID


class StorageProxy:
    def __init__(self, storage: BaseStorage,
                 user_id: int, chat_id: int,
                 state_groups: Dict[str, Type[StatesGroup]]):
        self.storage = storage
        self.state_groups = state_groups
        self.user_id = user_id
        self.chat_id = chat_id

    async def load_intent(self, intent_id: str) -> Intent:
        data = await self.storage.get_data(
            chat=self.chat_id,
            user=self._intent_key(intent_id)
        )
        if not data:
            raise ValueError(f"Unknown intent id: {intent_id}")
        data["state"] = self._state(data["state"])
        return Intent(**data)

    async def load_stack(self, stack_id: str = DEFAULT_STACK_ID) -> Stack:
        data = await self.storage.get_data(
            chat=self.chat_id,
            user=self._stack_key(stack_id)
        )
        if not data:
            return Stack(_id=stack_id)
        return Stack(**data)

    async def save_intent(self, intent: Optional[Intent]) -> None:
        if not intent:
            return
        data = copy(vars(intent))
        data["state"] = data["state"].state
        await self.storage.set_data(
            chat=self.chat_id,
            user=self._intent_key(intent.id),
            data=data,
        )

    async def remove_intent(self, intent_id: str):
        await self.storage.reset_data(chat=self.chat_id, user=self._intent_key(intent_id))

    async def remove_stack(self, stack_id: str):
        await self.storage.reset_data(chat=self.chat_id, user=self._stack_key(stack_id))

    async def save_stack(self, stack: Optional[Stack]) -> None:
        if not stack:
            return
        if stack.empty() and not stack.last_message_id:
            await self.storage.reset_data(
                chat=self.chat_id,
                user=self._stack_key(stack.id),
            )
        else:
            data = copy(vars(stack))
            await self.storage.set_data(
                chat=self.chat_id,
                user=self._stack_key(stack.id),
                data=data,
            )

    def _intent_key(self, intent_id: str) -> str:
        return f"{self.user_id}:aiogd:context:{intent_id}"

    def _stack_key(self, stack_id: str) -> str:
        return f"{self.user_id}:aiogd:stack:{stack_id}"

    def _state(self, state: str) -> State:
        group, *_ = state.partition(":")
        for real_state in self.state_groups[group].all_states:
            if real_state.state == state:
                return real_state
        raise ValueError(f"Unknown state {state}")
