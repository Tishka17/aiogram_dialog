from enum import Enum, auto
from typing import Dict, Any, Optional
from typing import Union, List

from aiogram.dispatcher.fsm.state import State
from aiogram.types import (
    Message, User, CallbackQuery, Chat, ChatMemberUpdated, TelegramObject, Update,
)

DIALOG_EVENT_NAME = "aiogd_update"
Data = Union[Dict, List, int, str, None]


class StartMode(Enum):
    NORMAL = auto()
    RESET_STACK = auto()
    NEW_STACK = auto()


class Action(Enum):
    DONE = "DONE"
    START = "START"
    UPDATE = "UPDATE"
    SWITCH = "SWITCH"


class DialogUpdateEvent(TelegramObject):
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = False

    from_user: User
    chat: Chat
    action: Action
    data: Any
    intent_id: Optional[str]
    stack_id: Optional[str]


class DialogStartEvent(DialogUpdateEvent):
    new_state: State
    mode: StartMode


class DialogSwitchEvent(DialogUpdateEvent):
    new_state: State


ChatEvent = Union[CallbackQuery, Message, DialogUpdateEvent, ChatMemberUpdated]


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
