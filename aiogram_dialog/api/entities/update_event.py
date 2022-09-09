from enum import Enum
from typing import Any, Optional

from aiogram.fsm.state import State
from aiogram.types import (
    Chat,
    TelegramObject,
    Update,
    User,
)

from .modes import (
    ShowMode,
    StartMode,
)

DIALOG_EVENT_NAME = "aiogd_update"


class DialogAction(Enum):
    DONE = "DONE"
    START = "START"
    UPDATE = "UPDATE"
    SWITCH = "SWITCH"


class DialogUpdateEvent(TelegramObject):
    class Config:
        """Pydantic config for custom event."""

        arbitrary_types_allowed = True
        use_enum_values = False
        copy_on_model_validation = False

    from_user: User
    chat: Chat
    action: DialogAction
    data: Any
    intent_id: Optional[str]
    stack_id: Optional[str]


class DialogStartEvent(DialogUpdateEvent):
    new_state: State
    mode: StartMode
    show_mode: ShowMode


class DialogSwitchEvent(DialogUpdateEvent):
    new_state: State


class DialogUpdate(Update):
    aiogd_update: DialogUpdateEvent

    def __init__(self, aiogd_update: DialogUpdateEvent):
        super().__init__(update_id=0, aiogd_update=aiogd_update)

    @property
    def event_type(self) -> str:
        return DIALOG_EVENT_NAME

    @property
    def event(self) -> DialogUpdateEvent:
        return self.aiogd_update
