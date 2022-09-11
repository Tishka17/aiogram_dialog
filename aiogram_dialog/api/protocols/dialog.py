from typing import Any, Optional, Protocol, Type

from aiogram import Router
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog.api.entities import (
    Data, LaunchMode,
)
from .manager import ActiveDialogManager


class DialogProtocol(Protocol):
    @property
    def launch_mode(self) -> LaunchMode:
        raise NotImplementedError

    def register(self, router: Router, *args, **kwargs) -> None:
        raise NotImplementedError

    def states_group_name(self) -> str:
        raise NotImplementedError

    def states_group(self) -> Type[StatesGroup]:
        raise NotImplementedError

    async def process_close(self, result: Any, manager: "ActiveDialogManager"):
        raise NotImplementedError

    async def process_start(
            self,
            manager: "ActiveDialogManager",
            start_data: Any,
            state: Optional[State] = None,
    ) -> None:
        raise NotImplementedError

    async def process_result(
            self, start_data: Data, result: Any,
            manager: "ActiveDialogManager",
    ) -> None:
        raise NotImplementedError

    async def next(self, manager: "ActiveDialogManager") -> None:
        raise NotImplementedError

    async def back(self, manager: "ActiveDialogManager") -> None:
        raise NotImplementedError

    async def switch_to(self, state: State,
                        manager: "ActiveDialogManager") -> None:
        raise NotImplementedError

    def find(self, widget_id) -> Any:
        raise NotImplementedError
