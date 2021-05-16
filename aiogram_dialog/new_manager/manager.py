from typing import Any, Optional, Dict

from aiogram.dispatcher.filters.state import State

from .manager_proto import ManagerProtocol, BaseManagerProtocol, StartMode
from ..context.intent import Intent, Data
from ..context.intent_filter import INTENT_KEY, STORAGE_KEY, STACK_KEY
from ..context.stack import DEFAULT_STACK_ID, Stack
from ..context.storage import StorageProxy
from ..manager.intent import ChatEvent
from ..manager.protocols import ManagedDialogProto, DialogRegistryProto


class IncorrectBackgroundError(RuntimeError):
    pass


class ManagerImpl(ManagerProtocol):
    def __init__(self, event: ChatEvent, registry: DialogRegistryProto, data: Dict):
        self.disabled = False
        self.registry = registry
        self.event = event
        self.data = data

    def check_disabled(self):
        if self.disabled:
            raise IncorrectBackgroundError(
                "Detected background access to dialog manager. "
                "Please use background manager available via `manager.bg()` "
                "method to access methods from background tasks"
            )

    def dialog(self) -> ManagedDialogProto:
        self.check_disabled()
        current = self.current_intent()
        if not current:
            raise RuntimeError
        return self.registry.find_dialog(current.state)

    async def _remove_kbd(self) -> None:
        pass

    def current_intent(self) -> Optional[Intent]:
        return self.data[INTENT_KEY]

    def current_stack(self) -> Optional[Stack]:
        return self.data[STACK_KEY]

    def storage(self) -> StorageProxy:
        return self.data[STORAGE_KEY]

    async def done(self, result: Any = None) -> None:
        await self.dialog().process_close(result, self)
        await self.mark_closed()
        intent = self.current_intent()
        if not intent:
            await self._remove_kbd()
            return
        dialog = self.dialog()
        await dialog.process_result(result, self)
        await dialog.show(self)

    async def mark_closed(self) -> None:
        self.check_disabled()
        storage = self.storage()
        stack = self.current_stack()
        await storage.remove_intent(stack.pop())
        if not stack.empty():
            intent_id = stack.last_intent_id()
            self.data[INTENT_KEY] = storage.load_intent(intent_id)

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
    ) -> None:
        self.check_disabled()
        storage = self.storage()
        if mode is StartMode.NORMAL:
            await self.storage().save_intent(self.current_intent())
            stack = self.current_stack()
            intent = stack.push(state, data)
            self.data[INTENT_KEY] = intent
            await self.dialog().process_start(self, data, state)
        elif mode is StartMode.RESET:
            stack = self.current_stack()
            while not stack.empty():
                await storage.remove_intent(stack.pop())
            return await self.start(state, data, StartMode.NORMAL)
        elif mode is StartMode.NEW_STACK:
            stack = Stack()
            await storage.save_stack(stack)
            await self.bg().start(state, data, StartMode.NORMAL)
        else:
            raise ValueError(f"Unknown start mode: {mode}")

    async def switch_to(self, state: State) -> None:
        self.check_disabled()
        intent = self.current_intent()
        if intent.state.group != state.group:
            raise ValueError(f"Cannot switch to another state group. "
                             f"Current state: {intent.state}, asked for {state}")
        intent.state = state
        await self.dialog().show(self)

    async def update(self, data: Dict) -> None:
        self.current_intent().data.update(data)
        await self.dialog().show(self)

    def bg(
            self,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            stack_id: str = DEFAULT_STACK_ID,
    ) -> "BaseManagerProtocol":
        pass

    async def close_manager(self) -> None:
        self.check_disabled()
        await self.storage().save_stack(self.current_stack())
        await self.storage().save_intent(self.current_intent())
        self.disabled = True
        del self.registry
        del self.event
        del self.data
