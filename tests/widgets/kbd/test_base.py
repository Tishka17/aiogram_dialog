import pytest
from aiogram import F
from aiogram.types import KeyboardButton

from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Keyboard


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
