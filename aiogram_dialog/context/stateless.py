from typing import Dict, Type, Optional

from aiogram.dispatcher.filters.state import State, StatesGroup

from .context import Context
from .stack import Stack, DEFAULT_STACK_ID
from ..exceptions import UnknownState


class StatelessContext(Context):
    @property
    def id(self):
        return self.state.state


class StatelessStorageProxy:
    def __init__(self,
                 user_id: int, chat_id: int,
                 state_groups: Dict[str, Type[StatesGroup]]):
        self.state_groups = state_groups
        self.user_id = user_id
        self.chat_id = chat_id
        self.intent_id = None

    async def new_intent_id(self, state: State) -> str:
        return state.state

    async def new_stack_id(self) -> str:
        raise DEFAULT_STACK_ID

    async def load_context(self, intent_id: str) -> Context:
        self.intent_id = intent_id
        return StatelessContext(
            _intent_id=intent_id,
            _stack_id=DEFAULT_STACK_ID,
            state=self._state(intent_id),
            start_data=None,
            dialog_data={},
            widget_data={},
        )

    async def load_stack(self, stack_id: str = DEFAULT_STACK_ID) -> Stack:
        if self.intent_id:
            intents = [self.intent_id]
        else:
            intents = []
        return Stack(_id=stack_id, intents=intents)

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


class StatelessStorageProxyFactory:
    def __init__(self, state_groups: Dict[str, Type[StatesGroup]]):
        self.state_groups = state_groups

    def __call__(self, user_id: int, chat_id: int) -> StatelessStorageProxy:
        return StatelessStorageProxy(
            user_id=user_id,
            chat_id=chat_id,
            state_groups=self.state_groups,
        )
