import asyncio
from asyncio import Event

import pytest
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ErrorEvent, Message

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.api.exceptions import OutdatedIntent
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format


class ClickSG(StatesGroup):
    MAIN = State()


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


async def start_click_dialog(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ClickSG.MAIN, mode=StartMode.RESET_STACK)


async def increment(callback, button, manager: DialogManager):
    count = manager.dialog_data.get("count", 0)
    await asyncio.sleep(0.01)
    manager.dialog_data["count"] = count + 1


async def finish(callback, button, manager: DialogManager):
    await asyncio.sleep(0.01)
    await manager.done()


async def click_getter(dialog_manager: DialogManager, **kwargs):
    return {"count": dialog_manager.dialog_data.get("count", 0)}


async def click_twice(on_click, dp: Dispatcher) -> MockMessageManager:
    dp.include_router(Dialog(Window(
        Format("count={count}"),
        Button(Const("click"), id="click", on_click=on_click),
        getter=click_getter,
        state=ClickSG.MAIN,
    )))
    dp.message.register(start_click_dialog, CommandStart())
    client = BotClient(dp)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    await client.send("/start")
    window = message_manager.last_message()
    locator = InlineButtonTextLocator("click")
    await asyncio.gather(
        client.click(window, locator),
        client.click(window, locator),
    )
    return message_manager


@pytest.mark.asyncio
async def test_concurrent_clicks_keep_dialog_data():
    dp = Dispatcher(storage=JsonMemoryStorage())
    message_manager = await click_twice(increment, dp)
    assert message_manager.last_message().text == "count=2"


@pytest.mark.asyncio
async def test_concurrent_click_after_done_is_outdated():
    errors = []

    async def on_error(event: ErrorEvent):
        errors.append(event.exception)

    dp = Dispatcher(storage=JsonMemoryStorage())
    dp.errors.register(on_error, ExceptionTypeFilter(Exception))
    await click_twice(finish, dp)
    assert [type(error) for error in errors] == [OutdatedIntent]
