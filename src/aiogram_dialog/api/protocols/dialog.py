from typing import Any, Dict, List, Optional, Protocol, runtime_checkable, Type

from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog.api.entities import (
    Data, LaunchMode, NewMessage,
)
from .manager import DialogManager


@runtime_checkable
class DialogProtocol(Protocol):
    @property
    def launch_mode(self) -> LaunchMode:
        raise NotImplementedError

    def states_group_name(self) -> str:
        raise NotImplementedError

    def states(self) -> List[State]:
        raise NotImplementedError

    def states_group(self) -> Type[StatesGroup]:
        raise NotImplementedError

    async def process_close(self, result: Any, manager: "DialogManager"):
        raise NotImplementedError

    async def process_start(
            self,
            manager: "DialogManager",
            start_data: Any,
            state: Optional[State] = None,
    ) -> None:
        raise NotImplementedError

    async def process_result(
            self, start_data: Data, result: Any,
            manager: "DialogManager",
    ) -> None:
        raise NotImplementedError

    def find(self, widget_id) -> Any:
        raise NotImplementedError

    async def load_data(
            self, manager: DialogManager,
    ) -> Dict:
        raise NotImplementedError

    async def render(self, manager: DialogManager) -> NewMessage:
        raise NotImplementedError
