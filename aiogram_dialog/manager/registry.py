import asyncio
from contextvars import copy_context
from typing import Sequence, Type, Dict

from aiogram import Dispatcher, Bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.handler import Handler
from aiogram.types import User, Chat

from .manager_middleware import ManagerMiddleware
from .protocols import ManagedDialogProto, DialogRegistryProto
from .update_handler import handle_update
from ..context.events import DialogUpdateEvent
from ..context.intent_filter import IntentFilter, IntentMiddleware


class DialogRegistry(DialogRegistryProto):
    def __init__(self, dp: Dispatcher, dialogs: Sequence[ManagedDialogProto] = ()):
        super().__init__()
        self.dp = dp
        self.dialogs = {
            d.states_group(): d for d in dialogs
        }
        self.state_groups: Dict[str, Type[StatesGroup]] = {
            d.states_group_name(): d.states_group() for d in dialogs
        }
        self.update_handler = Handler(dp, middleware_key="aiogd_update")
        self.register_update_handler(handle_update, state="*")
        self.dp.filters_factory.bind(IntentFilter)
        self.dp.setup_middleware(
            ManagerMiddleware(self)
        )
        self.dp.setup_middleware(
            IntentMiddleware(storage=dp.storage, state_groups=self.state_groups)
        )

    def register(self, dialog: ManagedDialogProto, *args, **kwargs):
        group = dialog.states_group()
        if group in self.dialogs:
            raise ValueError(f"StatesGroup `{group}` is already used")
        self.dialogs[group] = dialog
        self.state_groups[dialog.states_group_name()] = group
        dialog.register(
            self,
            self.dp,
            *args,
            aiogd_intent_state_group=group,
            **kwargs
        )

    def _register_middleware(self):
        self.dp.setup_middleware(self)

    def find_dialog(self, state: State) -> ManagedDialogProto:
        return self.dialogs[state.group]

    def register_update_handler(self, callback, *custom_filters, run_task=None, **kwargs) -> None:
        filters_set = self.dp.filters_factory.resolve(
            self.update_handler, *custom_filters, **kwargs
        )
        self.update_handler.register(
            self.dp._wrap_async_task(callback, run_task), filters_set
        )

    async def notify(self, event: DialogUpdateEvent) -> None:
        callback = lambda: asyncio.create_task(self._process_update(event))

        asyncio.get_running_loop().call_soon(
            callback,
            context=copy_context()
        )

    async def _process_update(self, event: DialogUpdateEvent):
        Bot.set_current(event.bot)
        User.set_current(event.from_user)
        Chat.set_current(event.chat)
        await self.update_handler.notify(event)
