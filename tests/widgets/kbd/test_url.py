import pytest

from aiogram_dialog.widgets.kbd import Url
from aiogram_dialog.widgets.text import Const


@pytest.mark.asyncio
async def test_render_url(mock_manager) -> None:
    url = Url(
        Const("Github"),
        Const("https://github.com/Tishka17/aiogram_dialog/"),
    )

    keyboard = await url.render_keyboard(data={}, manager=mock_manager)

    assert keyboard[0][0].text == "Github"
    assert keyboard[0][0].url == "https://github.com/Tishka17/aiogram_dialog/"
