from unittest.mock import patch

from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog.api.entities.stack import Stack, new_id

NOW = "aiogram_dialog.api.entities.stack.time.time"


class SG(StatesGroup):
    first = State()


def test_ids_within_one_second_are_unique():
    with patch(NOW, return_value=1_700_000_000):
        ids = [new_id() for _ in range(100)]
    assert len(set(ids)) == 100


def test_nested_intents_get_distinct_ids():
    with patch(NOW, return_value=1_700_000_000):
        stack = Stack()
        intents = [stack.push(state=SG.first, data=None).id for _ in range(3)]
    assert len({stack.id, *intents}) == 4
