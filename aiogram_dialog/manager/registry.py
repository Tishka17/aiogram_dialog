import asyncio
from contextvars import copy_context
from typing import Sequence, Type, Dict, Any, List, Union

from aiogram import Dispatcher, Bot, Router
from aiogram.dispatcher.event.bases import MiddlewareType
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.dispatcher.fsm.state import State, StatesGroup, any_state
from aiogram.types import User, Chat, Message, TelegramObject

from .manager_middleware import ManagerMiddleware
from .protocols import ManagedDialogProto, DialogRegistryProto, DialogManager
from .update_handler import handle_update
from ..context.events import DialogUpdateEvent, StartMode
from ..context.intent_filter import IntentFilter, IntentMiddleware

DIALOG_EVENT_NAME = "aiogd_update"


class DialogEventObserver(TelegramEventObserver):
    def _resolve_middlewares(self, *, outer: bool = False) -> List[MiddlewareType]:
        """
        Get all middlewares in a tree
        :param *:
        """
        middlewares = []
        if outer:
            middlewares.extend(self.outer_middlewares)
        else:
            for router in reversed(list(self.router.chain_head)):
                if router.observers.get(self.event_name):
                    observer = router.observers[self.event_name]
                    middlewares.extend(observer.middlewares)

        return middlewares


class DialogRouter(Router):
    def __init__(self, **kwargs: Any):
        super(DialogRouter, self).__init__(**kwargs)
        self.aiogd_update = self.observers[DIALOG_EVENT_NAME] = DialogEventObserver(
            router=self, event_name=DIALOG_EVENT_NAME
        )


class DialogRegistry(DialogRegistryProto):
    def __init__(self, dp: Dispatcher, dialogs: Sequence[ManagedDialogProto] = ()):
        super().__init__()
        self.dp = dp
        self.router = DialogRouter()
        self.dp.include_router(self.router)

        self.dialogs = {
            d.states_group(): d for d in dialogs
        }
        self.state_groups: Dict[str, Type[StatesGroup]] = {
            d.states_group_name(): d.states_group() for d in dialogs
        }
        self.update_handler = self.router.aiogd_update
        self.register_update_handler(handle_update, any_state)

        observer: TelegramEventObserver
        for observer in self.router.observers.values():
            observer.bind_filter(IntentFilter)

        self._register_middleware()

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
        async def start_dialog(m: Message, dialog_manager: DialogManager):
            await dialog_manager.start(state, mode=StartMode.RESET_STACK)

        self.router.message.register(start_dialog, any_state)

    def _register_middleware(self):
        self.dp.update.outer_middleware(
            ManagerMiddleware(self)
        )
        self.router.aiogd_update.outer_middleware(
            ManagerMiddleware(self)
        )

        self.dp.update.outer_middleware(
            IntentMiddleware(storage=self.dp.fsm.storage, state_groups=self.state_groups)
        )
        self.router.aiogd_update.outer_middleware(
            IntentMiddleware(storage=self.dp.fsm.storage, state_groups=self.state_groups)
        )

    def find_dialog(self, state: State) -> ManagedDialogProto:
        return self.dialogs[state.group]

    def register_update_handler(self, callback, *custom_filters, run_task=None,
                                **kwargs) -> None:  # ToDo run_task
        filters_set = self.update_handler.resolve_filters(kwargs)
        filters_set.append(*custom_filters)

        self.update_handler.register(
            callback, *filters_set
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
        await self.router.propagate_event(DIALOG_EVENT_NAME, event)
