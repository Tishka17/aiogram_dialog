from typing import Dict, Optional, Union

from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import Message, CallbackQuery

from .manager import Dialog, DialogManager
from .stack import DialogStack

ChatEvent = Union[CallbackQuery, Message]


class DialogRegistry(BaseMiddleware):
    dialogs: Dict[str, Dialog]

    def __init__(self, dp: Dispatcher, dialogs: Optional[Dict[str, Dialog]] = None):
        super().__init__()
        self.dp = dp
        if dialogs is None:
            dialogs = {}
        self.dialogs = dialogs

    def register(self, dialog: Dialog, *args, **kwargs):
        self.dialogs[dialog.states_group_name()] = dialog
        dialog.register(self.dp, *args, **kwargs)

    def _register_middleware(self):
        pass  # TODO

    def find_dialog(self, state: str) -> Dialog:
        group, *_ = state.partition(":")
        return self.dialogs[group]

    async def on_pre_process_message(self, event, data: dict):
        proxy = await FSMContextProxy.create(data["state"])
        manager = DialogManager(
            event,
            DialogStack(proxy),
            proxy,
            self,
        )
        data["manager"] = manager

    on_pre_process_callback_query = on_pre_process_message

    async def on_post_process_message(self, _, result, data: dict):
        manager: DialogManager = data.pop("manager")
        await manager.proxy.save()

    on_post_process_callback_query = on_post_process_message
