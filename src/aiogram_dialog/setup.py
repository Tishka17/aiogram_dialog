from typing import Callable, Dict, Iterable, Optional, Type, Union

from aiogram import Router
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.fsm.state import any_state, State, StatesGroup

from aiogram_dialog.api.entities import DIALOG_EVENT_NAME
from aiogram_dialog.api.exceptions import UnregisteredDialogError
from aiogram_dialog.api.internal import DialogManagerFactory
from aiogram_dialog.api.protocols import (
    BgManagerFactory, DialogProtocol, DialogRegistryProtocol,
    MediaIdStorageProtocol, MessageManagerProtocol,
)
from aiogram_dialog.context.intent_middleware import (
    context_saver_middleware,
    IntentErrorMiddleware,
    IntentMiddlewareFactory,
)
from aiogram_dialog.context.media_storage import MediaIdStorage
from aiogram_dialog.manager.bg_manager import BgManagerFactoryImpl
from aiogram_dialog.manager.manager_factory import DefaultManagerFactory
from aiogram_dialog.manager.manager_middleware import (
    BgFactoryMiddleware, ManagerMiddleware,
)
from aiogram_dialog.manager.message_manager import MessageManager
from aiogram_dialog.manager.update_handler import handle_update
from .about import about_dialog


def _setup_event_observer(router: Router) -> None:
    router.observers[DIALOG_EVENT_NAME] = TelegramEventObserver(
        router=router, event_name=DIALOG_EVENT_NAME,
    )


def _register_event_handler(router: Router, callback: Callable) -> None:
    handler = router.observers[DIALOG_EVENT_NAME]
    handler.register(callback, any_state)


class DialogRegistry(DialogRegistryProtocol):
    def __init__(self, router: Router):
        self.router = router
        self._loaded = False
        self._dialogs = {}
        self._state_groups = {}

    def _ensure_loaded(self):
        if not self._loaded:
            self.refresh()

    def find_dialog(self, state: Union[State, str]) -> DialogProtocol:
        self._ensure_loaded()
        try:
            return self._dialogs[state.group]
        except KeyError as e:
            raise UnregisteredDialogError(
                f"No dialog found for `{state.group}`"
                f" (looking by state `{state}`)",
            ) from e

    def state_groups(self) -> Dict[str, Type[StatesGroup]]:
        self._ensure_loaded()
        return self._state_groups

    def refresh(self):
        dialogs = collect_dialogs(self.router)
        self._dialogs = {d.states_group(): d for d in dialogs}
        self._state_groups = {
            d.states_group_name(): d.states_group()
            for d in self._dialogs.values()
        }
        self._loaded = True


def _startup_callback(
        registry: DialogRegistry,
) -> Callable:
    async def _setup_dialogs(router):
        registry.refresh()

    return _setup_dialogs


def _register_middleware(
        router: Router,
        dialog_manager_factory: DialogManagerFactory,
        bg_manager_factory: BgManagerFactory,
):
    registry = DialogRegistry(router)
    manager_middleware = ManagerMiddleware(
        dialog_manager_factory=dialog_manager_factory,
        router=router,
        registry=registry,
    )
    intent_middleware = IntentMiddlewareFactory(registry=registry)
    # delayed configuration of middlewares
    router.startup.register(_startup_callback(registry))
    update_handler = router.observers[DIALOG_EVENT_NAME]

    router.errors.middleware(IntentErrorMiddleware(registry=registry))

    router.message.middleware(manager_middleware)
    router.callback_query.middleware(manager_middleware)
    update_handler.middleware(manager_middleware)
    router.my_chat_member.middleware(manager_middleware)
    router.errors.middleware(manager_middleware)

    router.message.outer_middleware(intent_middleware.process_message)
    router.callback_query.outer_middleware(
        intent_middleware.process_callback_query,
    )
    update_handler.outer_middleware(
        intent_middleware.process_aiogd_update,
    )
    router.my_chat_member.outer_middleware(
        intent_middleware.process_my_chat_member,
    )

    router.message.middleware(context_saver_middleware)
    router.callback_query.middleware(context_saver_middleware)
    update_handler.middleware(context_saver_middleware)
    router.my_chat_member.middleware(context_saver_middleware)

    bg_factory_middleware = BgFactoryMiddleware(bg_manager_factory)
    for observer in router.observers.values():
        observer.outer_middleware(bg_factory_middleware)


def _prepare_dialog_manager_factory(
        dialog_manager_factory: Optional[DialogManagerFactory],
        message_manager: Optional[MessageManagerProtocol],
        media_id_storage: Optional[MediaIdStorageProtocol],
) -> DialogManagerFactory:
    if dialog_manager_factory is not None:
        return dialog_manager_factory
    if media_id_storage is None:
        media_id_storage = MediaIdStorage()
    if message_manager is None:
        message_manager = MessageManager()
    return DefaultManagerFactory(
        message_manager=message_manager,
        media_id_storage=media_id_storage,
    )


def collect_dialogs(router: Router) -> Iterable[DialogProtocol]:
    if isinstance(router, DialogProtocol):
        yield router
    for sub_router in router.sub_routers:
        yield from collect_dialogs(sub_router)


def _include_default_dialogs(router: Router):
    router.include_router(about_dialog())


def setup_dialogs(
        router: Router,
        *,
        dialog_manager_factory: Optional[DialogManagerFactory] = None,
        message_manager: Optional[MessageManagerProtocol] = None,
        media_id_storage: Optional[MediaIdStorageProtocol] = None,
) -> BgManagerFactory:
    _setup_event_observer(router)
    _register_event_handler(router, handle_update)
    _include_default_dialogs(router)

    dialog_manager_factory = _prepare_dialog_manager_factory(
        dialog_manager_factory=dialog_manager_factory,
        message_manager=message_manager,
        media_id_storage=media_id_storage,
    )
    bg_manager_factory = BgManagerFactoryImpl(router)
    _register_middleware(
        router=router,
        dialog_manager_factory=dialog_manager_factory,
        bg_manager_factory=bg_manager_factory,

    )
    return bg_manager_factory
