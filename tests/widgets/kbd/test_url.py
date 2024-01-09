from unittest.mock import Mock

import pytest
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.kbd import Url
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
async def test_render_url(mock_manager) -> None:
    url = Url(
        Const("Github"),
        Const("https://github.com/Tishka17/aiogram_dialog/"),
    )

    keyboard = await url.render_keyboard(data={}, manager=mock_manager)

    assert keyboard[0][0].text == "Github"
    assert keyboard[0][0].url == "https://github.com/Tishka17/aiogram_dialog/"
