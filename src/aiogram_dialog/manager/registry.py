import asyncio
from contextvars import copy_context
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Type

from aiogram import Bot, Dispatcher, Router
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.filters import Command
from aiogram.fsm.state import any_state, State, StatesGroup
from aiogram.types import Chat, Message, User

from aiogram_dialog.api.entities import (
    ChatEvent, DEFAULT_STACK_ID, DIALOG_EVENT_NAME, DialogUpdate, StartMode,
)
from aiogram_dialog.api.exceptions import UnregisteredDialogError
from aiogram_dialog.api.internal import (
    DialogManagerFactory, FakeChat, FakeUser,
)
from aiogram_dialog.api.protocols import (
    BaseDialogManager, DialogManager, DialogProtocol, DialogRegistryProtocol,
    DialogUpdaterProtocol, MediaIdStorageProtocol, MessageManagerProtocol,
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
from .bg_manager import BgManager
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
    ) -> None:
        self.message_manager = message_manager
        self.media_id_storage = media_id_storage

    def __call__(
            self, event: ChatEvent, data: Dict,
            registry: DialogRegistryProtocol,
            updater: DialogUpdaterProtocol,
    ) -> DialogManager:
        return ManagerImpl(
            event=event,
            data=data,
            message_manager=self.message_manager,
            media_id_storage=self.media_id_storage,
            registry=registry,
            updater=updater,
        )


@dataclass
class _DialogConfig:
    dialog: DialogProtocol
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    router: Optional[Router]


class _Updater(DialogUpdaterProtocol):
    def __init__(self, dp: Dispatcher):
        self.dp = dp

    async def notify(self, bot: Bot, update: DialogUpdate) -> None:
        def callback():
            asyncio.create_task(
                self._process_update(bot, update),
            )

        asyncio.get_running_loop().call_soon(callback, context=copy_context())

    async def _process_update(self, bot: Bot, update: DialogUpdate) -> None:
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


class DialogRegistry(DialogRegistryProtocol):
    def __init__(
            self,
            media_id_storage: Optional[MediaIdStorageProtocol] = None,
            message_manager: Optional[MessageManagerProtocol] = None,
            dialog_manager_factory: Optional[DialogManagerFactory] = None,
    ):
        if media_id_storage is None:
            media_id_storage = MediaIdStorage()
        if message_manager is None:
            message_manager = MessageManager()

        if dialog_manager_factory is None:
            dialog_manager_factory = DefaultManagerFactory(
                message_manager=message_manager,
                media_id_storage=media_id_storage,
            )
        self._dialog_manager_factory = dialog_manager_factory
        self.dialogs: Dict[Type[StatesGroup], _DialogConfig] = {}

    def register(
            self,
            dialog: DialogProtocol,
            *args: Any,
            router: Router = None,
            **kwargs: Any,
    ):
        group = dialog.states_group()
        if group in self.dialogs:
            raise ValueError(f"StatesGroup `{group}` is already used")
        self.dialogs[group] = _DialogConfig(
            dialog=dialog,
            router=router,
            args=args,
            kwargs=kwargs,
        )

    def find_dialog(self, state: State) -> DialogProtocol:
        try:
            return self.dialogs[state.group].dialog
        except KeyError as e:
            raise UnregisteredDialogError(
                f"No dialog found for `{state.group}`"
                f" (looking by state `{state}`)",
            ) from e

    def _state_groups(self) -> Dict[str, Type[StatesGroup]]:
        return {
            d.dialog.states_group_name(): d.dialog.states_group()
            for d in self.dialogs.values()
        }

    def register_start_handler(self, state: State, router: Router):
        async def start_dialog(
                message: Message, dialog_manager: DialogManager,
        ) -> None:
            await dialog_manager.start(state, mode=StartMode.RESET_STACK)

        router.message.register(
            start_dialog, Command(commands="start"), any_state,
        )

    def setup_dp(
            self,
            dp: Dispatcher,
            default_router: Optional[Router] = None,
    ):
        update_handler = DialogEventObserver(
            router=dp, event_name=DIALOG_EVENT_NAME,
        )
        dp.observers[DIALOG_EVENT_NAME] = update_handler
        self._register_update_handler(
            handle_update, update_handler,
        )
        self._register_middleware(dp, update_handler)

        if default_router is None:
            default_router = Router(name="aiogram_dialog_router")
        self._register_dialogs(dp, default_router)

    def _register_dialogs(self, dp: Dispatcher, default_router: Router):
        for group, dialog_config in self.dialogs.items():
            router = dialog_config.router or default_router
            dialog_config.dialog.register(
                router,
                IntentFilter(aiogd_intent_state_group=group),
                *dialog_config.args,
                **dialog_config.kwargs,
            )
        dp.include_router(default_router)

    def _register_update_handler(
            self, callback, update_handler: DialogEventObserver,
    ) -> None:
        update_handler.register(callback, any_state)

    def _register_middleware(
            self, dp: Dispatcher, update_handler: DialogEventObserver,
    ):
        state_groups = self._state_groups()
        manager_middleware = ManagerMiddleware(
            dialog_manager_factory=self._dialog_manager_factory,
            updater=_Updater(dp),
            registry=self,
        )
        intent_middleware = IntentMiddlewareFactory(
            storage=dp.fsm.storage, state_groups=state_groups,
        )
        dp.message.middleware(manager_middleware)
        dp.callback_query.middleware(manager_middleware)
        update_handler.middleware(manager_middleware)
        dp.my_chat_member.middleware(manager_middleware)
        dp.errors.middleware(manager_middleware)

        dp.message.outer_middleware(intent_middleware.process_message)
        dp.callback_query.outer_middleware(
            intent_middleware.process_callback_query,
        )
        update_handler.outer_middleware(
            intent_middleware.process_aiogd_update,
        )
        dp.my_chat_member.outer_middleware(
            intent_middleware.process_my_chat_member,
        )

        dp.message.middleware(context_saver_middleware)
        dp.callback_query.middleware(context_saver_middleware)
        update_handler.middleware(context_saver_middleware)
        dp.my_chat_member.middleware(context_saver_middleware)

        dp.errors.middleware(
            IntentErrorMiddleware(
                storage=dp.fsm.storage, state_groups=state_groups,
            ),
        )

    def bg(
            self,
            dp: Dispatcher,
            bot: Bot,
            user_id: int,
            chat_id: int,
            stack_id: str = DEFAULT_STACK_ID,
            intent_id: Optional[str] = None,
            load: bool = False,
    ) -> BaseDialogManager:
        return BgManager(
            user=FakeUser(id=user_id, is_bot=False, first_name=""),
            chat=FakeChat(id=chat_id, type=""),
            bot=bot,
            updater=_Updater(dp),
            intent_id=intent_id,
            stack_id=stack_id,
            load=load,
        )
