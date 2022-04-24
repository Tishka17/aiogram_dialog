from typing import Dict, Type, Optional

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import BaseStorage

from .context import Context
from .stack import Stack, DEFAULT_STACK_ID
from ..exceptions import UnknownState


class FakeStorageProxy:
    def __init__(self, storage: BaseStorage,
                 user_id: int, chat_id: int,
                 state_groups: Dict[str, Type[StatesGroup]]):
        self.storage = storage
        self.state_groups = state_groups
        self.user_id = user_id
        self.chat_id = chat_id

    async def new_intent_id(self, state: State) -> str:
        return str(state)

    async def new_stack_id(self) -> str:
        raise DEFAULT_STACK_ID

    async def load_context(self, intent_id: str) -> Context:
        return Context(
            _intent_id=intent_id,
            _stack_id=DEFAULT_STACK_ID,
            state=self._state(intent_id),
            start_data=None,
            dialog_data={},
            widget_data={},
        )

    async def load_stack(self, stack_id: str = DEFAULT_STACK_ID) -> Stack:
        return Stack(_id=stack_id)

    async def save_context(self, context: Optional[Context]) -> None:
        pass

    async def remove_context(self, intent_id: str):
        pass

    async def remove_stack(self, stack_id: str):
        pass

    async def save_stack(self, stack: Optional[Stack]) -> None:
        pass

    def _state(self, state: str) -> State:
        group, *_ = state.partition(":")
        for real_state in self.state_groups[group].all_states:
            if real_state.state == state:
                return real_state
        raise UnknownState(f"Unknown state {state}")
