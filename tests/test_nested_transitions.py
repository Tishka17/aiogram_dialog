import pytest
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

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
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const, Format


class MainSG(StatesGroup):
    start = State()


class SecondarySG(StatesGroup):
    start = State()


class ThirdSG(StatesGroup):
    start = State()


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


async def on_start_main(data, dialog_manager: DialogManager):
    await dialog_manager.start(SecondarySG.start)


async def on_start_sub(_, dialog_manager: DialogManager):
    await dialog_manager.start(ThirdSG.start)


async def on_process_result_sub(_, __, dialog_manager: DialogManager):
    await dialog_manager.done()


@pytest.fixture
def message_manager() -> MockMessageManager:
    return MockMessageManager()


@pytest.fixture
def client(dp) -> BotClient:
    return BotClient(dp)


@pytest.fixture
def dp(message_manager: MockMessageManager):
    dp = Dispatcher(storage=JsonMemoryStorage())
    dp.message.register(start, CommandStart())

    dp.include_router(Dialog(
        Window(
            Const("First"),
            state=MainSG.start,
        ),
        on_start=on_start_main,
    ))
    dp.include_router(Dialog(
        Window(
            Format("Subdialog"),
            Cancel(),
            state=SecondarySG.start,
        ),
        on_process_result=on_process_result_sub,
        on_start=on_start_sub,
    ))
    dp.include_router(Dialog(
        Window(
            Format("Third"),
            Cancel(),
            state=ThirdSG.start,
        ),
    ))
    setup_dialogs(dp, message_manager=message_manager)
    return dp


@pytest.mark.asyncio
async def test_start(dp, message_manager, client):
    # start
    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.text == "Third"
    assert first_message.reply_markup

    message_manager.reset_history()
    await client.click(first_message, InlineButtonTextLocator("Cancel"))
    second_message = message_manager.one_message()
    assert second_message.text == "First"
    assert second_message.reply_markup
