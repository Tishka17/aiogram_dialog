import random
import string
import time
from copy import copy
from typing import Dict, Type, Optional

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import BaseStorage

from .context import Context
from .stack import Stack, DEFAULT_STACK_ID
from ..exceptions import UnknownState, UnknownIntent

ID_SYMS = string.digits + string.ascii_letters


def new_int_id() -> int:
    return int(time.time()) % 100000000 + random.randint(0, 99) * 100000000


def id_to_str(int_id: int) -> str:
    if not int_id:
        return ID_SYMS[0]
    base = len(ID_SYMS)
    res = ""
    while int_id:
        int_id, mod = divmod(int_id, base)
        res += ID_SYMS[mod]
    return res


def new_id():
    return id_to_str(new_int_id())


class StorageProxy:
    def __init__(self, storage: BaseStorage,
                 user_id: int, chat_id: int,
                 state_groups: Dict[str, Type[StatesGroup]]):
        self.storage = storage
        self.state_groups = state_groups
        self.user_id = user_id
        self.chat_id = chat_id

    async def new_intent_id(self, state: State) -> str:
        return new_id()

    async def new_stack_id(self) -> str:
        return new_id()

    async def load_context(self, intent_id: str) -> Context:
        data = await self.storage.get_data(
            chat=self.chat_id,
            user=self._context_key(intent_id)
        )
        if not data:
            raise UnknownIntent(
                f"Context not found for intent id: {intent_id}")
        data["state"] = self._state(data["state"])
        return Context(**data)

    async def load_stack(self, stack_id: str = DEFAULT_STACK_ID) -> Stack:
        data = await self.storage.get_data(
            chat=self.chat_id,
            user=self._stack_key(stack_id)
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
            chat=self.chat_id,
            user=self._context_key(context.id),
            data=data,
        )

    async def remove_context(self, intent_id: str):
        await self.storage.reset_data(chat=self.chat_id,
                                      user=self._context_key(intent_id))

    async def remove_stack(self, stack_id: str):
        await self.storage.reset_data(chat=self.chat_id,
                                      user=self._stack_key(stack_id))

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

    def _context_key(self, intent_id: str) -> str:
        return f"{self.user_id}:aiogd:context:{intent_id}"

    def _stack_key(self, stack_id: str) -> str:
        return f"{self.user_id}:aiogd:stack:{stack_id}"

    def _state(self, state: str) -> State:
        group, *_ = state.partition(":")
        for real_state in self.state_groups[group].all_states:
            if real_state.state == state:
                return real_state
        raise UnknownState(f"Unknown state {state}")


class StorageProxyFactory:
    def __init__(self,
                 storage: BaseStorage,
                 state_groups: Dict[str, Type[StatesGroup]]):
        self.storage = storage
        self.state_groups = state_groups

    def __call__(
            self,
            user_id: int, chat_id: int,
            state_groups: Dict[str, Type[StatesGroup]]
    ):
        return StorageProxy(
            storage=self.storage,
            user_id=user_id,
            chat_id=chat_id,
            state_groups=self.state_groups,
        )
