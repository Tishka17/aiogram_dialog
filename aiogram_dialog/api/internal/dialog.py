from typing import Protocol

from .manager import InternalDialogManager


class DialogShowerProtocol(Protocol):
    async def show(self, manager: "InternalDialogManager") -> None:
        raise NotImplementedError
