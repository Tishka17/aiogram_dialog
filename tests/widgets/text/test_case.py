from unittest.mock import Mock

import pytest
from aiogram import F
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.text import Case, Const, Format


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
async def test_render_case(mock_manager) -> None:
    case = Case(
        {
            0: Format("{number} is even!"),
            1: Const("It is Odd"),
        },
        selector=F["number"] % 2,
    )

    rendered_text = await case.render_text(
        data={"number": 10}, manager=mock_manager,
    )

    assert rendered_text == "10 is even!"
