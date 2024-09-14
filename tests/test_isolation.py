import asyncio
from asyncio import Event

import pytest
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_dialog import setup_dialogs
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage


async def start(
        message: Message, data: list, event_common: Event,
):
    data.append(1)
    await event_common.wait()


@pytest.mark.asyncio
@pytest.mark.repeat(10)
async def test_concurrent_events():
    event_common = Event()
    data = []
    dp = Dispatcher(
        event_common=event_common,
        data=data,
        storage=JsonMemoryStorage(),
    )
    dp.message.register(start, CommandStart())

    client = BotClient(dp)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    # start
    t1 = asyncio.create_task(client.send("/start"))
    t2 = asyncio.create_task(client.send("/start"))
    await asyncio.sleep(0.1)
    assert len(data) == 1  # "Only single event expected to be processed"
    event_common.set()
    await t1
    await t2
    assert len(data) == 2
