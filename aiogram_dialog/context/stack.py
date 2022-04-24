import random
import string
import time
from dataclasses import dataclass, field
from typing import List, Optional

from aiogram.dispatcher.filters.state import State

from .events import Data
from .context import Context
from ..exceptions import DialogStackOverflow

DEFAULT_STACK_ID = ""
STACK_LIMIT = 100

@dataclass(unsafe_hash=True)
class Stack:
    _id: str = field(compare=True)
    intents: List[str] = field(compare=False, default_factory=list)
    last_message_id: Optional[int] = field(compare=False, default=None)
    last_media_id: Optional[str] = field(compare=False, default=None)
    last_media_unique_id: Optional[str] = field(compare=False, default=None)
    last_income_media_group_id: Optional[str] = field(compare=False, default=None)

    @property
    def id(self):
        return self._id

    def push(self, state: State, intent_id: str, data: Data) -> Context:
        if len(self.intents) >= STACK_LIMIT:
            raise DialogStackOverflow(
                f"Cannot open more dialogs in current stack. Max count is {STACK_LIMIT}"
            )
        context = Context(
            _intent_id=intent_id,
            _stack_id=self.id,
            state=state,
            start_data=data,
        )
        self.intents.append(context.id)
        return context

    def pop(self):
        return self.intents.pop()

    def last_intent_id(self):
        return self.intents[-1]

    def empty(self):
        return not self.intents

    def default(self):
        return self.id == DEFAULT_STACK_ID
