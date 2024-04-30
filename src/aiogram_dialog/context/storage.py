from copy import copy
from typing import Dict, Optional, Type

from aiogram import Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import BaseStorage, StorageKey

from aiogram_dialog.api.entities import DEFAULT_STACK_ID, Context, Stack
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState


class StorageProxy:
    def __init__(
        self,
        storage: BaseStorage,
        user_id: int,
        chat_id: int,
        bot: Bot,
        state_groups: Dict[str, Type[StatesGroup]],
    ):
        self.storage = storage
        self.state_groups = state_groups
        self.user_id = user_id
        self.chat_id = chat_id
        self.bot = bot

    async def load_context(self, intent_id: str) -> Context:
        data = await self.storage.get_data(
            key=self._context_key(intent_id),
        )
        if not data:
            raise UnknownIntent(
                f"Context not found for intent id: {intent_id}",
            )
        data["state"] = self._state(data["state"])
        return Context(**data)

    async def load_stack(self, stack_id: str = DEFAULT_STACK_ID) -> Stack:
        data = await self.storage.get_data(
            key=self._stack_key(stack_id),
        )
        if not data:
            return Stack(_id=stack_id)
        return Stack(**data)

    async def save_context(self, context: Optional[Context]) -> None:
        if not context:
            return
        data = copy(vars(context))
        data["state"] = data["state"].state
        await self.storage.set_data(
            key=self._context_key(context.id),
            data=data,
        )

    async def remove_context(self, intent_id: str) -> None:
        await self.storage.set_data(
            key=self._context_key(intent_id),
            data={},
        )

    async def remove_stack(self, stack_id: str) -> None:
        await self.storage.set_data(
            key=self._stack_key(stack_id),
            data={},
        )

    async def save_stack(self, stack: Optional[Stack]) -> None:
        if not stack:
            return
        if stack.empty() and not stack.last_message_id:
            await self.storage.set_data(
                key=self._stack_key(stack.id),
                data={},
            )
        else:
            data = copy(vars(stack))
            await self.storage.set_data(
                key=self._stack_key(stack.id),
                data=data,
            )

    def _context_key(self, intent_id: str) -> StorageKey:
        return StorageKey(
            bot_id=self.bot.id,
            chat_id=self.chat_id,
            user_id=self.user_id,
            destiny=f"aiogd:context:{intent_id}",
        )

    def _stack_key(self, stack_id: str) -> StorageKey:
        return StorageKey(
            bot_id=self.bot.id,
            chat_id=self.chat_id,
            user_id=self.user_id,
            destiny=f"aiogd:stack:{stack_id}",
        )

    def _state(self, state: str) -> State:
        group, *_ = state.partition(":")
        try:
            for real_state in self.state_groups[group].__all_states__:
                if real_state.state == state:
                    return real_state
        except KeyError:
            raise UnknownState(f"Unknown state group {group}")
        raise UnknownState(f"Unknown state {state}")
