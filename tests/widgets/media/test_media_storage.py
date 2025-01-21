import os
import tempfile

import pytest
from aiogram.enums import ContentType

from aiogram_dialog.context.media_storage import MediaIdStorage


@pytest.mark.asyncio
async def test_get_media_id():
    manager = MediaIdStorage()
    with tempfile.NamedTemporaryFile() as file:
        os.fsync(file)
        media_id = await manager.get_media_id(
            file.name,
            None,
            ContentType.DOCUMENT,
        )
        assert media_id is None

        await manager.save_media_id(
            file.name,
            None,
            ContentType.DOCUMENT,
            "test1",
        )

        media_id = await manager.get_media_id(
            file.name,
            None,
            ContentType.DOCUMENT,
        )
        assert media_id == "test1"

        file.write(b"new info")
        file.flush()

        media_id = await manager.get_media_id(
            file.name,
            None,
            ContentType.DOCUMENT,
        )
        assert media_id is None
