import pytest
from aiogram import F

from aiogram_dialog.widgets.text import Const, Format, TextCase


@pytest.mark.asyncio
async def test_render_case(mock_manager) -> None:
    case = TextCase(
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
