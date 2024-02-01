from abc import abstractmethod
from typing import Dict, Protocol, Type, Union

from aiogram.fsm.state import State, StatesGroup

from .dialog import DialogProtocol


class DialogRegistryProtocol(Protocol):
    @abstractmethod
    def find_dialog(self, state: Union[State, str]) -> DialogProtocol:
        raise NotImplementedError

    @abstractmethod
    def states_groups(self) -> Dict[str, Type[StatesGroup]]:
        raise NotImplementedError
