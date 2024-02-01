import pytest

from aiogram_dialog.widgets.text import Const, Multi


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
