from typing import Any, Optional, Protocol

from aiogram.fsm.state import State


class ManagedDialogProtocol(Protocol):
    async def show(self):
        raise NotImplementedError

    async def next(self):
        raise NotImplementedError

    async def back(self):
        raise NotImplementedError

    async def switch_to(self, state: State):
        raise NotImplementedError

    def find(self, widget_id) -> Optional[Any]:
        raise NotImplementedError
