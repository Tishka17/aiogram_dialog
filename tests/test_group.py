import asyncio
from typing import Any

import pytest
from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.api.entities import GROUP_STACK_ID, AccessSettings
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format


class MainSG(StatesGroup):
    start = State()


window = Window(
    Format("stub"),
    Button(Const("Button"), id="btn"),
    state=MainSG.start,
)


async def start(event: Any, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


async def start_shared(event: Any, dialog_manager: DialogManager):
    dialog_manager = dialog_manager.bg(stack_id=GROUP_STACK_ID)
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


async def add_shared(event: Any, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, access_settings=AccessSettings(
        user_ids=[1, 2],
    ))


@pytest.fixture
def message_manager():
    return MockMessageManager()


@pytest.fixture
def dp(message_manager):
    dp = Dispatcher(storage=JsonMemoryStorage())
    dp.include_router(Dialog(window))
    setup_dialogs(dp, message_manager=message_manager)
    return dp


@pytest.fixture
def client(dp):
    return BotClient(dp, chat_id=-1, user_id=1, chat_type="group")


@pytest.fixture
def second_client(dp):
    return BotClient(dp, chat_id=-1, user_id=2, chat_type="group")


@pytest.mark.asyncio
async def test_second_user(dp, client, second_client, message_manager):
    dp.message.register(start, CommandStart())
    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.text == "stub"
    message_manager.reset_history()
    await second_client.send("test")
    assert not message_manager.sent_messages
    await second_client.click(
        first_message, InlineButtonTextLocator("Button"),
    )
    assert not message_manager.sent_messages


@pytest.mark.asyncio
async def test_change_settings(dp, client, second_client, message_manager):
    dp.message.register(start, CommandStart())
    dp.message.register(add_shared, Command("add"))

    await client.send("/start")
    message_manager.reset_history()

    await client.send("/add")
    window_message = message_manager.one_message()
    message_manager.reset_history()

    await second_client.click(
        window_message, InlineButtonTextLocator("Button"),
    )
    window_message = message_manager.one_message()
    message_manager.reset_history()
    assert window_message.text == "stub"

    await client.send("/start")
    window_message = message_manager.one_message()
    message_manager.reset_history()

    await second_client.click(
        window_message, InlineButtonTextLocator("Button"),
    )
    assert not message_manager.sent_messages


@pytest.mark.asyncio
async def test_change_settings_bg(dp, client, second_client, message_manager):
    dp.message.register(start, CommandStart())
    dp.message.register(add_shared, Command("add"))

    await client.send("/start")
    message_manager.reset_history()

    await client.send("/add")
    window_message = message_manager.one_message()
    message_manager.reset_history()

    await second_client.click(
        window_message, InlineButtonTextLocator("Button"),
    )
    window_message = message_manager.one_message()
    message_manager.reset_history()
    assert window_message.text == "stub"

    await client.send("/start")
    window_message = message_manager.one_message()
    message_manager.reset_history()

    await second_client.click(
        window_message, InlineButtonTextLocator("Button"),
    )
    assert not message_manager.sent_messages


@pytest.mark.asyncio
async def test_same_user(dp, client, message_manager):
    dp.message.register(start, CommandStart())
    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.text == "stub"
    message_manager.reset_history()
    await client.send("test")
    assert not message_manager.sent_messages  # no resend
    await client.click(
        first_message, InlineButtonTextLocator("Button"),
    )
    first_message = message_manager.one_message()
    assert first_message.text == "stub"


@pytest.mark.asyncio
async def test_shared_stack(dp, client, second_client, message_manager):
    dp.message.register(start_shared, CommandStart())
    await client.send("/start")
    await asyncio.sleep(0.02)  # synchronization workaround, fixme

    first_message = message_manager.one_message()
    assert first_message.text == "stub"
    message_manager.reset_history()
    await second_client.send("test")
    assert not message_manager.sent_messages
    await second_client.click(
        first_message, InlineButtonTextLocator("Button"),
    )
    second_message = message_manager.one_message()
    assert second_message.text == "stub"
