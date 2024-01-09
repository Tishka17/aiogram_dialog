from unittest.mock import Mock

import pytest
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.kbd import Button, Row
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
async def test_render_row(mock_manager) -> None:
    row = Row(
        Button(Const("1"), id="first"),
        Button(Const("2"), id="second"),
        Button(Const("3"), id="third"),
    )

    keyboard = await row.render_keyboard(data={}, manager=mock_manager)

    assert len(keyboard) == 1

    assert len(keyboard[0]) == 3

    assert keyboard[0][0].text == "1"
    assert keyboard[0][1].text == "2"
    assert keyboard[0][2].text == "3"
