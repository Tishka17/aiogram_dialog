from typing import Any, Dict, Optional, Protocol

from aiogram.fsm.state import State

from aiogram_dialog.api.entities import (
    ChatEvent, Data, ShowMode, StartMode, Context, Stack,
)
from .managed import ManagedDialogProtocol


class BaseDialogManager(Protocol):
    @property
    def event(self) -> ChatEvent:
        raise NotImplementedError

    async def done(self, result: Any = None) -> None:
        raise NotImplementedError

    async def mark_closed(self) -> None:
        raise NotImplementedError

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
            show_mode: ShowMode = ShowMode.AUTO,
    ) -> None:
        raise NotImplementedError

    async def switch_to(self, state: State) -> None:
        raise NotImplementedError

    async def update(self, data: Dict) -> None:
        raise NotImplementedError

    def bg(
            self,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            stack_id: Optional[str] = None,
            load: bool = False,  # load chat and user
    ) -> "BaseDialogManager":
        raise NotImplementedError


class ActiveDialogManager(BaseDialogManager, Protocol):

    @property
    def data(self) -> Dict:
        """Middleware data"""
        raise NotImplementedError

    @property
    def show_mode(self) -> ShowMode:
        """Get current show mode, used for next show action."""
        raise NotImplementedError

    @show_mode.setter
    def show_mode(self, show_mode: ShowMode) -> None:
        """Set current show mode, used for next show action."""
        raise NotImplementedError

    def current_context(self) -> Optional[Context]:
        raise NotImplementedError

    def current_stack(self) -> Optional[Stack]:
        raise NotImplementedError

    def dialog(self) -> ManagedDialogProtocol:
        raise NotImplementedError

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        raise NotImplementedError
