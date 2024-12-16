from abc import abstractmethod
from typing import Protocol, Union

from aiogram.fsm.state import State, StatesGroup

from .dialog import DialogProtocol


class DialogRegistryProtocol(Protocol):
    @abstractmethod
    def find_dialog(self, state: Union[State, str]) -> DialogProtocol:
        raise NotImplementedError

    @abstractmethod
    def states_groups(self) -> dict[str, type[StatesGroup]]:
        raise NotImplementedError
