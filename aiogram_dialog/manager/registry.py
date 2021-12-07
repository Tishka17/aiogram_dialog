import asyncio
from contextvars import copy_context
from typing import Sequence, Type, Dict, Optional

from aiogram import Dispatcher, Bot, Router
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.fsm.state import State, StatesGroup, any_state
from aiogram.types import User, Chat, Message

from .manager_middleware import ManagerMiddleware
from .protocols import (
    ManagedDialogProto, DialogRegistryProto, DialogManager,
    MediaIdStorageProtocol,
)
from .update_handler import handle_update
from ..context.events import StartMode, DIALOG_EVENT_NAME, DialogUpdate
from ..context.intent_filter import IntentFilter, IntentMiddleware
from ..context.media_storage import MediaIdStorage


class DialogEventObserver(TelegramEventObserver):
    pass


class DialogRegistry(DialogRegistryProto):
    def __init__(
            self,
            dp: Dispatcher,
            dialogs: Sequence[ManagedDialogProto] = (),
            media_id_storage: Optional[MediaIdStorageProtocol] = None,
    ):
        self.dp = dp
        self.update_handler = self.dp.observers[DIALOG_EVENT_NAME] = DialogEventObserver(
            router=self.dp, event_name=DIALOG_EVENT_NAME
        )

        self.dialogs = {
            d.states_group(): d for d in dialogs
        }
        self.state_groups: Dict[str, Type[StatesGroup]] = {
            d.states_group_name(): d.states_group() for d in dialogs
        }
        self.register_update_handler(handle_update, any_state)

        observer: TelegramEventObserver
        for observer in self.dp.observers.values():
            observer.bind_filter(IntentFilter)

        self._register_middleware()
        if media_id_storage is None:
            media_id_storage = MediaIdStorage()
        self._media_id_storage = media_id_storage

    @property
    def media_id_storage(self) -> MediaIdStorageProtocol:
        return self._media_id_storage

    def register(self, dialog: ManagedDialogProto, *args, router: Router = None, **kwargs):
        group = dialog.states_group()
        if group in self.dialogs:
            raise ValueError(f"StatesGroup `{group}` is already used")
        self.dialogs[group] = dialog
        self.state_groups[dialog.states_group_name()] = group
        dialog.register(
            self,
            router if router else self.dp,
            *args,
            aiogd_intent_state_group=group,
            **kwargs
        )

    def register_start_handler(self, state: State):
        async def start_dialog(m: Message, dialog_manager: DialogManager):
            await dialog_manager.start(state, mode=StartMode.RESET_STACK)

        self.dp.message.register(start_dialog, Command(commands="start"), any_state)

    def _register_middleware(self):
        self.dp.update.outer_middleware(
            ManagerMiddleware(self)
        )
        self.dp.update.outer_middleware(
            IntentMiddleware(storage=self.dp.fsm.storage, state_groups=self.state_groups)
        )

    def find_dialog(self, state: State) -> ManagedDialogProto:
        return self.dialogs[state.group]

    def register_update_handler(self, callback, *custom_filters, **kwargs) -> None:
        self.update_handler.register(
            callback, *custom_filters, **kwargs
        )

    async def notify(self, bot: Bot, update: DialogUpdate) -> None:
        callback = lambda: asyncio.create_task(self._process_update(bot, update))

        asyncio.get_running_loop().call_soon(
            callback,
            context=copy_context()
        )

    async def _process_update(self, bot: Bot, update: DialogUpdate):
        event = update.event
        Bot.set_current(bot)
        User.set_current(event.from_user)
        Chat.set_current(event.chat)
        await self.dp.propagate_event(
            update_type="update",
            event=update,
            bot=bot,
            event_from_user=event.from_user,
            event_chat=event.chat,
        )
