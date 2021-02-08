from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Dict, Optional, Any
from typing import Union, List

from aiogram import Bot
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, User, CallbackQuery, Chat

Data = Union[Dict, List, int, str, None]


@dataclass(frozen=True)
class Intent:
    id: str = field(compare=True)
    name: str = field(compare=False)
    data: Data = field(compare=False)


class Action(Enum):
    DONE = "DONE"
    START = "START"
    UPDATE = "UPDATE"
    SWITCH = "SWITCH"


@dataclass
class DialogUpdateEvent:
    bot: Bot
    from_user: User
    chat: Chat
    message: Optional[Message]
    action: Action
    current_intent: Intent
    data: Any


@dataclass
class DialogStartEvent(DialogUpdateEvent):
    new_state: State
    reset_stack: bool


@dataclass
class DialogSwitchEvent(DialogUpdateEvent):
    new_state: State


ChatEvent = Union[CallbackQuery, Message, DialogUpdateEvent]
