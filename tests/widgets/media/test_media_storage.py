import asyncio
import os
import tempfile

import pytest
from aiogram.enums import ContentType

from aiogram_dialog.context.media_storage import MediaIdStorage


@pytest.mark.asyncio
async def test_get_media_id():
    manager = MediaIdStorage()
    with tempfile.TemporaryDirectory() as d:
        filename = os.path.join(d, "file_test")  # noqa: PTH118
        media_id = await manager.get_media_id(
            filename,
            None,
            ContentType.DOCUMENT,
        )
        assert media_id is None

        with open(filename, "w") as file:  # noqa: PTH123
            file.write("test1")

        await manager.save_media_id(
            filename,
            None,
            ContentType.DOCUMENT,
            "test1",
        )

        media_id = await manager.get_media_id(
            filename,
            None,
            ContentType.DOCUMENT,
        )
        assert media_id == "test1"

        await asyncio.sleep(0.1)

        with open(filename, "w") as file:  # noqa: PTH123
            file.write("test2")

        media_id = await manager.get_media_id(
            filename,
            None,
            ContentType.DOCUMENT,
        )
        assert media_id is None
