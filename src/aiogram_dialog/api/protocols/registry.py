from typing import Protocol, Union

from aiogram.fsm.state import State

from .dialog import DialogProtocol


class DialogRegistryProtocol(Protocol):
    def find_dialog(self, state: Union[State, str]) -> DialogProtocol:
        raise NotImplementedError
