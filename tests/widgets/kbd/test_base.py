from unittest.mock import Mock

import pytest
from aiogram import F
from aiogram.fsm.state import State
from aiogram.types import KeyboardButton

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Keyboard


@pytest.fixture()
def mock_manager() -> DialogManager:
    manager = Mock()
    context = Context(
        dialog_data={},
        start_data={},
        widget_data={},
        state=State(),
        _stack_id="_stack_id",
        _intent_id="_intent_id",
    )
    manager.current_context = Mock(side_effect=lambda: context)

    return manager


class Button(Keyboard):
    def __init__(self, id: str, when: WhenCondition = None):
        super().__init__(when=when, id=id)

    async def _render_keyboard(
            self,
            data,
            manager: DialogManager,
    ) -> RawKeyboard:
        return [[KeyboardButton(text=self.widget_id)]]


@pytest.mark.asyncio
async def test_or(mock_manager):
    text = Button("a") | Button("b")
    res = await text.render_keyboard({}, mock_manager)
    assert res == [[KeyboardButton(text="a")]]


@pytest.mark.asyncio
async def test_or_condition(mock_manager):
    text = (
        Button("A", when=F["a"]) |
        Button("B", when=F["b"]) |
        Button("C")
    )
    res = await text.render_keyboard({"a": True}, mock_manager)
    assert res == [[KeyboardButton(text="A")]]
    res = await text.render_keyboard({"b": True}, mock_manager)
    assert res == [[KeyboardButton(text="B")]]
    res = await text.render_keyboard({}, mock_manager)
    assert res == [[KeyboardButton(text="C")]]
