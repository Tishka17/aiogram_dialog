from typing import Optional, Any

from aiogram.dispatcher.filters.state import State

from .context import Context
from .stack import Stack

FORBID = object()


class ContextCompat:
    def __init__(self, context: Context, stack: Stack):
        self.context = context
        self.stack = stack

    @property
    def state(self) -> State:
        return self.context.state

    @state.setter
    def state(self, state: State):
        self.context.state = state

    @property
    def last_message_id(self) -> Optional[int]:
        return self.stack.last_message_id

    @last_message_id.setter
    def last_message_id(self, last_message_id: Optional[int]):
        self.stack.last_message_id = last_message_id

    def set_data(self, key: str, value: Any, *, internal: bool = False):
        if internal:
            self.context.widget_data[key] = value
        else:
            self.context.dialog_data[key] = value

    def data(self, key, default=FORBID, *, internal: bool = False, ):
        if internal:
            data = self.context.widget_data
        else:
            data = self.context.dialog_data
        if default is FORBID:
            return data[key]
        else:
            return data.get(key, default)
