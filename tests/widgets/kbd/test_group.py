import itertools
from unittest.mock import Mock

import pytest
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardButton

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const


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


@pytest.mark.asyncio
async def test_render_group(mock_manager) -> None:
    group = Group(
        Button(Const("1"), id="first"),
        Button(Const("2"), id="second"),
        Button(Const("3"), id="third"),
        Button(Const("4"), id="fourth"),
        Button(Const("5"), id="fifth"),
        width=3,
    )

    keyboard = await group.render_keyboard(data={}, manager=mock_manager)

    assert len(keyboard[0]) == 3
    assert len(keyboard[1]) == 2

    buttons: list[InlineKeyboardButton] = list(
        itertools.chain.from_iterable(keyboard),
    )

    assert len(buttons) == 5

    assert buttons[0].text == "1"
    assert buttons[1].text == "2"
    assert buttons[2].text == "3"
    assert buttons[3].text == "4"
    assert buttons[4].text == "5"
