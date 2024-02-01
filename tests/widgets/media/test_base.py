import pytest
from aiogram import F
from aiogram.enums import ContentType

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.media import Media


class Static(Media):
    def __init__(self, path: str, when: WhenCondition = None):
        super().__init__(when=when)
        self.path = path

    async def _render_media(
            self,
            data,
            manager: DialogManager,
    ) -> MediaAttachment:
        return MediaAttachment(ContentType.PHOTO, path=self.path)


@pytest.mark.asyncio
async def test_or(mock_manager):
    text = Static("a") | Static("b")
    res = await text.render_media({}, mock_manager)
    assert res == MediaAttachment(ContentType.PHOTO, path="a")


@pytest.mark.asyncio
async def test_or_condition(mock_manager):
    text = (
        Static("A", when=F["a"]) |
        Static("B", when=F["b"]) |
        Static("C")
    )
    res = await text.render_media({"a": True}, mock_manager)
    assert res == MediaAttachment(ContentType.PHOTO, path="A")
    res = await text.render_media({"b": True}, mock_manager)
    assert res == MediaAttachment(ContentType.PHOTO, path="B")
    res = await text.render_media({}, mock_manager)
    assert res == MediaAttachment(ContentType.PHOTO, path="C")
