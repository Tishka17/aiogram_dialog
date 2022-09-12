from typing import Dict, Protocol

from aiogram_dialog.api.protocols import DialogProtocol, ManagedDialogProtocol
from .manager import InternalDialogManager


class DialogShowerProtocol(DialogProtocol, Protocol):
    async def show(self, manager: "InternalDialogManager") -> None:
        raise NotImplementedError

    async def load_data(
            self, manager: InternalDialogManager,
    ) -> Dict:
        raise NotImplementedError

    def managed(
            self, manager: "InternalDialogManager",
    ) -> ManagedDialogProtocol:
        raise NotImplementedError
