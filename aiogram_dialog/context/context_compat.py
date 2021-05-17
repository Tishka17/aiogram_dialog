from typing import Optional, Any

from aiogram.dispatcher.filters.state import State

from .intent import Intent
from .stack import Stack

FORBID = object()


class ContextCompat:
    def __init__(self, intent: Intent, stack: Stack):
        self.intent = intent
        self.stack = stack

    @property
    def state(self) -> State:
        return self.intent.state

    @state.setter
    def state(self, state: State):
        self.intent.state = state

    @property
    def last_message_id(self) -> Optional[int]:
        return self.stack.last_message_id

    @last_message_id.setter
    def last_message_id(self, last_message_id: Optional[int]):
        self.stack.last_message_id = last_message_id

    def set_data(self, key: str, value: Any, *, internal: bool = False):
        if internal:
            self.intent.widget_data[key] = value
        else:
            self.intent.dialog_data[key] = value

    def data(self, key, default=FORBID, *, internal: bool = False, ):
        if internal:
            data = self.intent.widget_data
        else:
            data = self.intent.dialog_data
        if default is FORBID:
            return data[key]
        else:
            return data.get(key, default)
