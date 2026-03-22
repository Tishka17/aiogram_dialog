from typing import Any

import pytest
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
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


async def start_for_second_user(
        event: Any, dialog_manager: DialogManager,
) -> None:
    async with dialog_manager.bg(user_id=2, chat_id=-1).fg() as manager:
        await manager.start(MainSG.start, mode=StartMode.RESET_STACK)


async def start_for_second_user_via_bg(
        event: Any, dialog_manager: DialogManager,
) -> None:
    async with dialog_manager.bg(user_id=2, chat_id=-1).fg() as manager:
        await manager.start(MainSG.start, mode=StartMode.RESET_STACK)


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
async def test_start_in_foreground_for_another_user(
        dp, client, second_client, message_manager,
):
    dp.message.register(start_for_second_user, CommandStart())

    await client.send("/start")
    window_message = message_manager.one_message()
    assert window_message.text == "stub"
    message_manager.reset_history()

    await client.click(
        window_message, InlineButtonTextLocator("Button"),
    )
    assert not message_manager.sent_messages
    message_manager.reset_history()

    await second_client.click(
        window_message, InlineButtonTextLocator("Button"),
    )
    second_message = message_manager.one_message()
    assert second_message.text == "stub"


@pytest.mark.asyncio
async def test_start_in_foreground_for_another_user_via_bg(
        dp, client, second_client, message_manager,
):
    dp.message.register(start_for_second_user_via_bg, CommandStart())

    await client.send("/start")
    window_message = message_manager.one_message()
    assert window_message.text == "stub"
    message_manager.reset_history()

    await client.click(
        window_message, InlineButtonTextLocator("Button"),
    )
    assert not message_manager.sent_messages
    message_manager.reset_history()

    await second_client.click(
        window_message, InlineButtonTextLocator("Button"),
    )
    second_message = message_manager.one_message()
    assert second_message.text == "stub"
