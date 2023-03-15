from typing import Callable, Type, Dict, Optional, Union, Iterable

from aiogram import Router
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.fsm.state import any_state, StatesGroup, State

from aiogram_dialog.api.entities import DIALOG_EVENT_NAME
from aiogram_dialog.api.exceptions import UnregisteredDialogError
from aiogram_dialog.api.internal import DialogManagerFactory
from aiogram_dialog.api.protocols import (
    DialogRegistryProtocol, DialogProtocol,
    MessageManagerProtocol, MediaIdStorageProtocol,
)
from aiogram_dialog.context.intent_middleware import (
    context_saver_middleware,
    IntentErrorMiddleware,
    IntentMiddlewareFactory,
)
from aiogram_dialog.context.media_storage import MediaIdStorage
from .manager_factory import DefaultManagerFactory
from .manager_middleware import ManagerMiddleware
from .message_manager import MessageManager
from .update_handler import handle_update
from .updater import Updater


def _setup_event_observer(router: Router) -> None:
    dialog_update_handler = TelegramEventObserver(
        router=router, event_name=DIALOG_EVENT_NAME,
    )
    router.observers[DIALOG_EVENT_NAME] = dialog_update_handler


def _register_event_handler(router: Router, callback: Callable) -> None:
    handler = router.observers[DIALOG_EVENT_NAME]
    handler.register(callback, any_state)


def _register_middleware(
        router: Router,
        state_groups: Dict[str, Type[StatesGroup]],
        registry: DialogRegistryProtocol,
        dialog_manager_factory: DialogManagerFactory,
):
    manager_middleware = ManagerMiddleware(
        dialog_manager_factory=dialog_manager_factory,
        updater=Updater(router),
        registry=registry,
    )
    update_handler = router.observers[DIALOG_EVENT_NAME]

    router.message.middleware(manager_middleware)
    router.callback_query.middleware(manager_middleware)
    update_handler.middleware(manager_middleware)
    router.my_chat_member.middleware(manager_middleware)
    router.errors.middleware(manager_middleware)

    intent_middleware = IntentMiddlewareFactory(state_groups=state_groups)
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

    router.errors.middleware(IntentErrorMiddleware(state_groups=state_groups))


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


class DialogRegistry(DialogRegistryProtocol):
    def __init__(self, dialogs: Iterable[DialogProtocol]):
        self.dialogs = {d.states_group(): d for d in dialogs}

    def find_dialog(self, state: Union[State, str]) -> DialogProtocol:
        try:
            return self.dialogs[state.group]
        except KeyError as e:
            raise UnregisteredDialogError(
                f"No dialog found for `{state.group}`"
                f" (looking by state `{state}`)",
            ) from e

    def state_groups(self) -> Dict[str, Type[StatesGroup]]:
        return {
            d.states_group_name(): d.states_group()
            for d in self.dialogs.values()
        }


def _collect_dialogs(router: Router) -> Iterable[DialogProtocol]:
    if isinstance(router, DialogProtocol):
        yield router
    for sub_router in router.sub_routers:
        yield from _collect_dialogs(sub_router)


def setup_dialogs(
        router: Router,
        *,
        dialog_manager_factory: Optional[DialogManagerFactory] = None,
        message_manager: Optional[MessageManagerProtocol] = None,
        media_id_storage: Optional[MediaIdStorageProtocol] = None,
):
    _setup_event_observer(router)
    _register_event_handler(router, handle_update)

    dialog_manager_factory = _prepare_dialog_manager_factory(
        dialog_manager_factory=dialog_manager_factory,
        message_manager=message_manager,
        media_id_storage=media_id_storage,
    )
    registry = DialogRegistry(_collect_dialogs(router))
    _register_middleware(
        router=router,
        state_groups=registry.state_groups(),
        registry=registry,
        dialog_manager_factory=dialog_manager_factory,
    )
