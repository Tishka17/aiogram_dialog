from abc import abstractmethod
from typing import Any, Dict, Protocol, Union

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message

from aiogram_dialog import ChatEvent, DialogManager
from aiogram_dialog.api.entities import Data, MarkupVariant, NewMessage
from aiogram_dialog.api.entities.context import DataDict
from aiogram_dialog.api.protocols import DialogProtocol


class WindowProtocol(Protocol):
    @abstractmethod
    async def render_text(
        self,
        data: Dict[str, Union[DataDict, Dict[str, Any], ChatEvent]],
        manager: DialogManager,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def render_kbd(
        self,
        data: Dict[str, Union[DataDict, Dict[str, Any], ChatEvent]],
        manager: DialogManager,
    ) -> MarkupVariant:
        raise NotImplementedError

    @abstractmethod
    async def load_data(
        self,
        dialog: "DialogProtocol",
        manager: DialogManager,
    ) -> Dict[str, Union[DataDict, Dict[str, Any], ChatEvent]]:
        raise NotImplementedError

    @abstractmethod
    async def process_message(
        self,
        message: Message,
        dialog: "DialogProtocol",
        manager: DialogManager,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def process_callback(
        self,
        callback: CallbackQuery,
        dialog: "DialogProtocol",
        manager: DialogManager,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def process_result(
        self,
        start_data: Data,
        result: Any,
        manager: "DialogManager",
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def render(
        self,
        dialog: "DialogProtocol",
        manager: DialogManager,
    ) -> NewMessage:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> State:
        raise NotImplementedError

    @abstractmethod
    def find(self, widget_id: str) -> Any:
        raise NotImplementedError
