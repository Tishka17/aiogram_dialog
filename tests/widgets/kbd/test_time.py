import datetime

import pytest
from aiogram.types import TelegramObject

from aiogram_dialog.widgets.kbd import TimeSelect


@pytest.mark.asyncio
async def test_render_time_select(mock_manager) -> None:
    select = TimeSelect(
        "x",
    )

    keyboard = await select.render_keyboard(
        data={}, manager=mock_manager,
    )

    assert len(keyboard) == 8

    await select.set_value(
        TelegramObject(),
        mock_manager,
        datetime.time(0, 10),
    )

    keyboard = await select.render_keyboard(
        data={}, manager=mock_manager,
    )

    assert len(keyboard) == 8
