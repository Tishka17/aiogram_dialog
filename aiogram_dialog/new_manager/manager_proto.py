from enum import Enum, auto
from typing import Any, Optional, Protocol, Dict

from aiogram.dispatcher.filters.state import State

from ..context.intent import Intent, Data
from ..context.stack import DEFAULT_STACK_ID
from ..manager.protocols import ManagedDialogProto


class StartMode(Enum):
    NORMAL = auto()
    RESET = auto()
    NEW_STACK = auto()


class BaseManagerProtocol(Protocol):
    def current_intent(self) -> Intent:
        pass

    async def done(self, result: Any = None) -> None:
        pass

    async def mark_closed(self) -> None:
        pass

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
    ) -> None:
        pass

    async def switch_to(self, state: State) -> None:
        pass

    async def update(self, data: Dict) -> None:
        pass

    def bg(
            self,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            stack_id: str = DEFAULT_STACK_ID,
    ) -> "BaseManagerProtocol":
        pass


class ManagerProtocol(BaseManagerProtocol):

    def dialog(self) -> ManagedDialogProto:
        pass

    async def close_manager(self) -> None:
        pass
