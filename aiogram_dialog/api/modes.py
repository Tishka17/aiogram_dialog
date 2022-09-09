from enum import Enum


class ShowMode(Enum):
    AUTO = "auto"
    EDIT = "edit"
    SEND = "send"


class StartMode(Enum):
    NORMAL = "NORMAL"
    RESET_STACK = "RESET_STACK"
    NEW_STACK = "NEW_STACK"


class Action(Enum):
    DONE = "DONE"
    START = "START"
    UPDATE = "UPDATE"
    SWITCH = "SWITCH"
