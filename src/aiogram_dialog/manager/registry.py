import asyncio
from contextvars import copy_context
from typing import Dict, Optional, Sequence, Type

from aiogram import Bot, Dispatcher, Router
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.filters import Command
from aiogram.fsm.state import any_state, State, StatesGroup
from aiogram.types import Chat, Message, User

from aiogram_dialog.api.entities import (
    ChatEvent, DIALOG_EVENT_NAME, DialogUpdate, StartMode,
)
from aiogram_dialog.api.exceptions import UnregisteredDialogError
from aiogram_dialog.api.internal import (
    DialogManagerFactory,
)
from aiogram_dialog.api.protocols import (
    DialogManager, DialogProtocol, DialogRegistryProtocol,
    MediaIdStorageProtocol, MessageManagerProtocol,
)
from aiogram_dialog.context.intent_filter import (
    IntentFilter,
)
from aiogram_dialog.context.intent_middleware import (
    context_saver_middleware,
    IntentErrorMiddleware,
    IntentMiddlewareFactory,
)
from aiogram_dialog.context.media_storage import MediaIdStorage
from .manager import ManagerImpl
from .manager_middleware import ManagerMiddleware
from .message_manager import MessageManager
from .update_handler import handle_update


class DialogEventObserver(TelegramEventObserver):
    pass


class DefaultManagerFactory(DialogManagerFactory):
    def __init__(
            self,
            message_manager: MessageManagerProtocol,
            media_id_storage: MediaIdStorageProtocol,
            registry: DialogRegistryProtocol,
    ):
        self.message_manager = message_manager
        self.media_id_storage = media_id_storage
        self.registry = registry

    def __call__(self, event: ChatEvent, data: Dict) -> DialogManager:
        return ManagerImpl(
            event=event,
            data=data,
            message_manager=self.message_manager,
            media_id_storage=self.media_id_storage,
            registry=self.registry,
        )


class DialogRegistry(DialogRegistryProtocol):
    def __init__(
            self,
            dp: Dispatcher,
            dialogs: Sequence[DialogProtocol] = (),
            media_id_storage: Optional[MediaIdStorageProtocol] = None,
            message_manager: Optional[MessageManagerProtocol] = None,
            dialog_manager_factory: Optional[DialogManagerFactory] = None,
            default_router: Optional[Router] = None,
    ):
        self.dp = dp
        self.update_handler = self.dp.observers[
            DIALOG_EVENT_NAME
        ] = DialogEventObserver(router=self.dp, event_name=DIALOG_EVENT_NAME)
        self.default_router = (
            default_router
            if default_router
            else dp.include_router(Router(name="aiogram_dialog_router"))
        )

        self.dialogs = {d.states_group(): d for d in dialogs}
        self.state_groups: Dict[str, Type[StatesGroup]] = {
            d.states_group_name(): d.states_group() for d in dialogs
        }
        self.register_update_handler(handle_update, any_state)

        if media_id_storage is None:
            media_id_storage = MediaIdStorage()
        self._media_id_storage = media_id_storage
        if message_manager is None:
            message_manager = MessageManager()
        self._message_manager = message_manager
        if dialog_manager_factory is None:
            dialog_manager_factory = DefaultManagerFactory(
                message_manager=message_manager,
                media_id_storage=media_id_storage,
                registry=self,
            )
        self.dialog_manager_factory = dialog_manager_factory
        self._register_middleware()

    @property
    def media_id_storage(self) -> MediaIdStorageProtocol:
        return self._media_id_storage

    @property
    def message_manager(self) -> MessageManagerProtocol:
        return self._message_manager

    def register(
            self,
            dialog: DialogProtocol,
            *args,
            router: Router = None,
            **kwargs,
    ):
        group = dialog.states_group()
        if group in self.dialogs:
            raise ValueError(f"StatesGroup `{group}` is already used")
        self.dialogs[group] = dialog
        self.state_groups[dialog.states_group_name()] = group
        dialog.register(
            router if router else self.default_router,
            IntentFilter(aiogd_intent_state_group=group),
            *args,
            **kwargs,
        )

    def register_start_handler(self, state: State):
        async def start_dialog(
                message: Message, dialog_manager: DialogManager,
        ) -> None:
            await dialog_manager.start(state, mode=StartMode.RESET_STACK)

        self.dp.message.register(
            start_dialog, Command(commands="start"), any_state,
        )

    def _register_middleware(self):
        manager_middleware = ManagerMiddleware(
            dialog_manager_factory=self.dialog_manager_factory,
        )
        intent_middleware = IntentMiddlewareFactory(
            storage=self.dp.fsm.storage, state_groups=self.state_groups,
        )
        self.dp.message.middleware(manager_middleware)
        self.dp.callback_query.middleware(manager_middleware)
        self.update_handler.middleware(manager_middleware)
        self.dp.my_chat_member.middleware(manager_middleware)
        self.dp.errors.middleware(manager_middleware)

        self.dp.message.outer_middleware(intent_middleware.process_message)
        self.dp.callback_query.outer_middleware(
            intent_middleware.process_callback_query,
        )
        self.update_handler.outer_middleware(
            intent_middleware.process_aiogd_update,
        )
        self.dp.my_chat_member.outer_middleware(
            intent_middleware.process_my_chat_member,
        )

        self.dp.message.middleware(context_saver_middleware)
        self.dp.callback_query.middleware(context_saver_middleware)
        self.update_handler.middleware(context_saver_middleware)
        self.dp.my_chat_member.middleware(context_saver_middleware)

        self.dp.errors.middleware(
            IntentErrorMiddleware(
                storage=self.dp.fsm.storage, state_groups=self.state_groups,
            ),
        )

    def find_dialog(self, state: State) -> DialogProtocol:
        try:
            return self.dialogs[state.group]
        except KeyError as e:
            raise UnregisteredDialogError(
                f"No dialog found for `{state.group}`"
                f" (looking by state `{state}`)",
            ) from e

    def register_update_handler(
            self, callback, *custom_filters, **kwargs,
    ) -> None:
        self.update_handler.register(callback, *custom_filters, **kwargs)

    async def notify(self, bot: Bot, update: DialogUpdate) -> None:
        def callback():
            asyncio.create_task(
                self._process_update(bot, update),
            )

        asyncio.get_running_loop().call_soon(callback, context=copy_context())

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
