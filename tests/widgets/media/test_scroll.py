from unittest.mock import Mock

import pytest

from aiogram_dialog.widgets.media import MediaScroll, StaticMedia
from aiogram_dialog.widgets.text import Format


@pytest.mark.asyncio
async def test_render_media_scroll(mock_manager):
    media = MediaScroll(
        items=["0.png", "1.png", "2.png"],
        media=StaticMedia(path=Format("/{item}")),
        id="m",
    )
    res = await media.render_media(data={}, manager=mock_manager)
    assert res.path == "/0.png"

    await media.set_page(event=Mock(), page=2, manager=mock_manager)
    res = await media.render_media(data={}, manager=mock_manager)
    assert res.path == "/2.png"

    managed = media.managed(mock_manager)
    await managed.set_page(1)
    res = await media.render_media(data={}, manager=mock_manager)
    assert res.path == "/1.png"
