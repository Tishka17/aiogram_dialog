import random
import string
import time
from dataclasses import asdict
from typing import Optional, List

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.storage import FSMContextProxy

from .intent import Data, Intent

TASK_STACK = "__AIOGD_TASKS"
ID_SYMS = string.digits + string.ascii_letters


def new_id() -> int:
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


class DialogStack:
    def __init__(self, proxy: FSMContextProxy):
        self.proxy = proxy
        self.proxy.setdefault(TASK_STACK, [])

    @classmethod
    async def create(cls, state: FSMContext):
        proxy = await FSMContextProxy.create(state)
        return cls(proxy)

    def _stack(self) -> List:
        return self.proxy[TASK_STACK]

    def push(self, name: str, data: Data) -> Intent:
        # TODO check stack size overflow and data overflow
        intent = Intent(id_to_str(new_id()), name, data)
        self._stack().append(asdict(intent))
        return intent

    def current(self) -> Optional[Intent]:
        stack = self._stack()
        if not stack:
            return None
        return Intent(**stack[-1])

    def pop(self, intent: Optional[Intent] = None):
        stack = self._stack()
        if intent is None:
            stack.pop()
        else:
            stack.remove(intent)

    def clear(self):
        self._stack().clear()


if __name__ == '__main__':
    print(id_to_str(10000000000 - 1))
    stack = DialogStack({})
    print(stack.push("hello", 1))
    print(stack._stack())
    print(stack.proxy)
    print(stack.current())
