import operator
from unittest.mock import Mock

import pytest
from aiogram.fsm.state import State
from aiogram.types import TelegramObject

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.kbd import Toggle
from aiogram_dialog.widgets.text import Format


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
async def test_render_toggle(mock_manager) -> None:
    toggle = Toggle(
        Format("{item[1]}"),
        id="fruit",
        item_id_getter=operator.itemgetter(0),
        items=[("1", "Apple"), ("2", "Banana"), ("3", "Orange")],
    )

    keyboard = await toggle.render_keyboard(
        data={}, manager=mock_manager,
    )

    assert keyboard[0][0].text == "Apple"

    await toggle.set_checked(TelegramObject(), "2", mock_manager)

    keyboard = await toggle.render_keyboard(
        data={}, manager=mock_manager,
    )

    assert keyboard[0][0].text == "Banana"
