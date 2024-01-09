from unittest.mock import Mock

import pytest
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.kbd import Button, Column
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
async def test_render_column(mock_manager) -> None:
    column = Column(
        Button(Const("1"), id="first"),
        Button(Const("2"), id="second"),
        Button(Const("3"), id="third"),
    )

    keyboard = await column.render_keyboard(data={}, manager=mock_manager)

    assert len(keyboard) == 3

    assert len(keyboard[0]) == 1
    assert keyboard[0][0].text == "1"

    assert len(keyboard[1]) == 1
    assert keyboard[1][0].text == "2"

    assert len(keyboard[2]) == 1
    assert keyboard[2][0].text == "3"
