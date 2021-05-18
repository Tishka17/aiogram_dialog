import random
import string
import time
from dataclasses import dataclass, field
from typing import List, Optional

from aiogram.dispatcher.filters.state import State

from .intent import Intent, Data

DEFAULT_STACK_ID = ""
STACK_LIMIT = 100
ID_SYMS = string.digits + string.ascii_letters


def new_int_id() -> int:
    return int(time.time()) % 100000000 + random.randint(0, 99) * 100000000


def id_to_str(int_id: int) -> str:
    if not int_id:
        return ID_SYMS[0]
    base = len(ID_SYMS)
    res = ""
    while int_id:
        int_id, mod = divmod(int_id, base)
        res += ID_SYMS[mod]
    return res


def new_id():
    return id_to_str(new_int_id())


@dataclass(unsafe_hash=True)
class Stack:
    _id: str = field(compare=True, default_factory=new_id)
    intents: List[str] = field(compare=False, default_factory=list)
    last_message_id: Optional[int] = field(compare=False, default=None)

    @property
    def id(self):
        return self._id

    def push(self, state: State, data: Data) -> Intent:
        if len(self.intents) >= STACK_LIMIT:
            raise RuntimeError(f"Task stack overflow. Max size is {STACK_LIMIT}")
        intent = Intent(
            _id=new_id(),
            _stack_id=self.id,
            state=state,
            start_data=data,
        )
        self.intents.append(intent.id)
        return intent

    def pop(self):
        return self.intents.pop()

    def last_intent_id(self):
        return self.intents[-1]

    def empty(self):
        return not self.intents

    def default(self):
        return self.id == DEFAULT_STACK_ID
