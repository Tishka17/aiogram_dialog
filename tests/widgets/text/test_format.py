import pytest

from aiogram_dialog.widgets.text import Format


@pytest.mark.asyncio
async def test_render_format(mock_manager) -> None:
    format_widget = Format("Hello, {name}!")

    rendered_text = await format_widget.render_text(
        data={"name": "Tishka17"}, manager=mock_manager,
    )

    assert rendered_text == "Hello, Tishka17!"
