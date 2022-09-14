from typing import Protocol, Union

from aiogram import Bot
from aiogram.fsm.state import State

from aiogram_dialog.api.entities import DialogUpdate
from .dialog import DialogProtocol


class DialogRegistryProtocol(Protocol):
    def find_dialog(self, state: Union[State, str]) -> DialogProtocol:
        pass

    async def notify(self, bot: Bot, update: DialogUpdate) -> None:
        pass
