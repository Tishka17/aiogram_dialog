__all__ = [
    "DEFAULT_STACK_ID",
    "Dialog",
    "Data",
    "ChatEvent",
    "LaunchMode",
    "StartMode",
    "BaseDialogManager",
    "BgManagerFactory",
    "DialogManager",
    "DialogProtocol",
    "setup_dialogs",
    "ShowMode",
    "SubManager",
    "Window",
]

import importlib.metadata as _metadata

from .api.entities import (
    ChatEvent, Data, DEFAULT_STACK_ID, LaunchMode, ShowMode, StartMode,
)
from .api.protocols import (
    BaseDialogManager, BgManagerFactory, DialogManager, DialogProtocol,
)
from .dialog import Dialog
from .manager.sub_manager import SubManager
from .setup import setup_dialogs
from .window import Window

__version__ = _metadata.version("aiogram-dialog")
