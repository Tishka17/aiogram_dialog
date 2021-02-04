from typing import Dict, Optional, Union

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.storage import FSMContextProxy

from .manager import Dialog, DialogManager
from .stack import DialogStack


class DialogRegistry(BaseMiddleware):
    dialogs: Dict[str, Dialog]

    def __init__(self, dp: Dispatcher, dialogs: Optional[Dict[str, Dialog]] = None):
        super().__init__()
        self.dp = dp
        if dialogs is None:
            dialogs = {}
        self.dialogs = dialogs
        self._register_middleware()

    def register(self, dialog: Dialog, *args, **kwargs):
        name = dialog.states_group_name()
        if name in self.dialogs:
            raise ValueError(f"StatesGroup `{name}` is already used")
        self.dialogs[name] = dialog
        dialog.register(self.dp, *args, **kwargs)

    def _register_middleware(self):
        self.dp.setup_middleware(self)

    def find_dialog(self, state: Union[str, State]) -> Dialog:
        if isinstance(state, str):
            group, *_ = state.partition(":")
        else:
            group = state.group.__full_group_name__
        return self.dialogs[group]

    async def on_pre_process_message(self, event, data: dict):
        proxy = await FSMContextProxy.create(self.dp.current_state())  # there is no state in data at this moment
        manager = DialogManager(
            event,
            DialogStack(proxy),
            proxy,
            self,
            data,
        )
        data["dialog_manager"] = manager

    on_pre_process_callback_query = on_pre_process_message

    async def on_post_process_message(self, _, result, data: dict):
        manager: DialogManager = data.pop("dialog_manager")
        await manager.proxy.save()

    on_post_process_callback_query = on_post_process_message
