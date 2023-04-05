from typing import Protocol, Union, Dict, Type

from aiogram.fsm.state import State, StatesGroup

from .dialog import DialogProtocol


class DialogRegistryProtocol(Protocol):
    def find_dialog(self, state: Union[State, str]) -> DialogProtocol:
        raise NotImplementedError

    def state_groups(self) -> Dict[str, Type[StatesGroup]]:
        raise NotImplementedError
