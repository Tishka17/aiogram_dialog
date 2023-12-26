from unittest.mock import Mock

import pytest
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.media import MediaScroll, StaticMedia
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
