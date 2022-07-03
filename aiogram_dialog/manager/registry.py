import asyncio
from contextvars import copy_context
from typing import Sequence, Type, Dict, Optional

from aiogram import Dispatcher, Bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.handler import Handler
from aiogram.types import User, Chat, Message

from .manager import ManagerImpl
from .manager_middleware import ManagerMiddleware
from .protocols import (
    ManagedDialogProto, DialogRegistryProto, DialogManager,
    MediaIdStorageProtocol, MessageManagerProtocol, DialogManagerFactory,
)
from .update_handler import handle_update
from ..context.events import DialogUpdateEvent, StartMode
from ..context.intent_filter import IntentFilter, IntentMiddleware
from ..context.media_storage import MediaIdStorage
from ..exceptions import UnregisteredDialogError
from ..message_manager import MessageManager


class DialogRegistry(DialogRegistryProto):
    def __init__(
            self,
            dp: Dispatcher,
            dialogs: Sequence[ManagedDialogProto] = (),
            media_id_storage: Optional[MediaIdStorageProtocol] = None,
            message_manager: Optional[MessageManagerProtocol] = None,
            dialog_manager_factory: DialogManagerFactory = ManagerImpl,
    ):
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
        self.dialog_manager_factory = dialog_manager_factory
        self._register_middleware()
        if media_id_storage is None:
            media_id_storage = MediaIdStorage()
        self._media_id_storage = media_id_storage
        if message_manager is None:
            message_manager = MessageManager()
        self._message_manager = message_manager

    @property
    def media_id_storage(self) -> MediaIdStorageProtocol:
        return self._media_id_storage

    @property
    def message_manager(self) -> MessageManagerProtocol:
        return self._message_manager

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

    def register_start_handler(self, state: State):
        @self.dp.message_handler(commands=["start"], state="*")
        async def start_dialog(m: Message, dialog_manager: DialogManager):
            await dialog_manager.start(state, mode=StartMode.RESET_STACK)

    def _register_middleware(self):
        self.dp.setup_middleware(
            ManagerMiddleware(self, self.dialog_manager_factory)
        )
        self.dp.setup_middleware(
            IntentMiddleware(storage=self.dp.storage, state_groups=self.state_groups)
        )

    def find_dialog(self, state: State) -> ManagedDialogProto:
        try:
            return self.dialogs[state.group]
        except KeyError as e:
            raise UnregisteredDialogError(
                f"No dialog found for `{state.group}`"
                f" (looking by state `{state}`)"
            ) from e

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
