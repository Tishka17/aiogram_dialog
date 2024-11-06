__all__ = [
    "AccessSettings",
    "DEFAULT_STACK_ID",
    "Dialog",
    "Data",
    "GROUP_STACK_ID",
    "ChatEvent",
    "LaunchMode",
    "StartMode",
    "BaseDialogManager",
    "BgManagerFactory",
    "CancelEventProcessing",
    "DialogManager",
    "DialogProtocol",
    "UnsetId",
    "setup_dialogs",
    "ShowMode",
    "SubManager",
    "Window",
]

import importlib.metadata as _metadata

from .api.entities import (
    DEFAULT_STACK_ID,
    GROUP_STACK_ID,
    AccessSettings,
    ChatEvent,
    Data,
    LaunchMode,
    ShowMode,
    StartMode,
)
from .api.protocols import (
    BaseDialogManager,
    BgManagerFactory,
    CancelEventProcessing,
    DialogManager,
    DialogProtocol,
    UnsetId,
)
from .dialog import Dialog
from .manager.sub_manager import SubManager
from .setup import setup_dialogs
from .window import Window

__version__ = _metadata.version("aiogram-dialog")
