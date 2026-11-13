from unittest.mock import patch

from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog.api.entities.stack import _STACK_LIMIT, Stack

NOW = "aiogram_dialog.api.entities.stack.time.time"
RANDINT = "aiogram_dialog.api.entities.stack.random.randint"


class SG(StatesGroup):
    first = State()


def test_push_skips_an_id_already_in_the_stack():
    stack = Stack()
    with (
        patch(NOW, return_value=1_700_000_000),
        patch(RANDINT, side_effect=[7, 7, 8]),
    ):
        first = stack.push(state=SG.first, data=None).id
        second = stack.push(state=SG.first, data=None).id
    assert first != second


def test_full_stack_pushed_in_one_second_has_distinct_ids():
    stack = Stack()
    with patch(NOW, return_value=1_700_000_000):
        for _ in range(_STACK_LIMIT):
            stack.push(state=SG.first, data=None)
    assert len(set(stack.intents)) == _STACK_LIMIT
