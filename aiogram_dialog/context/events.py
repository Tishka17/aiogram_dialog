from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, Optional
from typing import Union, List

from aiogram import Bot
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, User, CallbackQuery, Chat

Data = Union[Dict, List, int, str, None]


class StartMode(Enum):
    NORMAL = auto()
    RESET = auto()
    NEW_STACK = auto()


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
    action: Action
    data: Any
    intent_id: Optional[str]
    stack_id: Optional[str]


@dataclass
class DialogStartEvent(DialogUpdateEvent):
    new_state: State
    mode: StartMode


@dataclass
class DialogSwitchEvent(DialogUpdateEvent):
    new_state: State


ChatEvent = Union[CallbackQuery, Message, DialogUpdateEvent]
