import pytest

from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const


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
