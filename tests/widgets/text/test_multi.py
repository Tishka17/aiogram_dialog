from unittest.mock import Mock

import pytest
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.text import Const, Multi


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
async def test_render_multi(mock_manager) -> None:
    multi = Multi(
        Const("Hello!"),
        Const("And goodbye!"),
        sep=" ",
    )

    rendered_text = await multi.render_text(
        data={}, manager=mock_manager,
    )

    assert rendered_text == "Hello! And goodbye!"
