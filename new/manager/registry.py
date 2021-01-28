from typing import Dict, Protocol, Optional

from aiogram import Dispatcher


class Dialog(Protocol):
    def register(self, dp: Dispatcher, *args, **kwargs):
        pass

    def states_group_name(self) -> str:
        pass


class DialogRegistry:
    dialogs: Dict[str, Dialog]

    def __init__(self, dp: Dispatcher, dialogs: Optional[Dict[str, Dialog]] = None):
        self.dp = dp
        if dialogs is None:
            dialogs = {}
        self.dialogs = dialogs

    def register(self, dialog: Dialog, *args, **kwargs):
        self.dialogs[dialog.states_group_name()] = dialog
        dialog.register(self.dp, *args, **kwargs)
