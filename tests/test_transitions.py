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
from aiogram_dialog.widgets.kbd import Back, Cancel, Next, Start
from aiogram_dialog.widgets.text import Const, Format


class MainSG(StatesGroup):
    start = State()
    next = State()


class SecondarySG(StatesGroup):
    start = State()


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


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
            Next(),
            Start(Const("Start"), state=SecondarySG.start, id="start"),
            Cancel(),
            state=MainSG.start,
        ),
        Window(
            Const("Second"),
            Back(),
            state=MainSG.next,
        ),
    ))
    dp.include_router(Dialog(
        Window(
            Format("Subdialog"),
            Cancel(),
            state=SecondarySG.start,
        ),
    ))
    setup_dialogs(dp, message_manager=message_manager)
    return dp


@pytest.mark.asyncio
async def test_start(dp, message_manager, client):
    # start
    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.text == "First"
    assert first_message.reply_markup


@pytest.mark.asyncio
async def test_next_back(dp, message_manager, client):
    await client.send("/start")
    first_message = message_manager.one_message()

    # click next
    message_manager.reset_history()
    callback_id = await client.click(
        first_message, InlineButtonTextLocator("Next"),
    )
    message_manager.assert_answered(callback_id)
    second_message = message_manager.one_message()
    assert second_message.text == "Second"

    # click back
    message_manager.reset_history()
    callback_id = await client.click(
        second_message, InlineButtonTextLocator("Back"),
    )
    message_manager.assert_answered(callback_id)
    last_message = message_manager.one_message()
    assert last_message.text == "First"
    assert last_message.reply_markup


@pytest.mark.asyncio
async def test_finish_last(dp, message_manager, client):
    await client.send("/start")
    first_message = message_manager.one_message()

    # click back
    message_manager.reset_history()
    callback_id = await client.click(
        first_message, InlineButtonTextLocator("Cancel"),
    )
    message_manager.assert_answered(callback_id)
    last_message = message_manager.one_message()
    assert not last_message.reply_markup, "Keyboard closed"


@pytest.mark.asyncio
async def test_reset_stack(dp, message_manager, client):
    for _ in range(200):
        message_manager.reset_history()
        await client.send("/start")
        first_message = message_manager.one_message()
        assert first_message.text == "First"

    message_manager.reset_history()
    callback_id = await client.click(
        first_message, InlineButtonTextLocator("Cancel"),
    )
    message_manager.assert_answered(callback_id)
    last_message = message_manager.one_message()
    assert not last_message.reply_markup, "Keyboard closed"


@pytest.mark.asyncio
async def test_subdialog(dp, message_manager, client):
    await client.send("/start")
    first_message = message_manager.one_message()

    # start subdialog
    message_manager.reset_history()
    callback_id = await client.click(
        first_message, InlineButtonTextLocator("Start"),
    )
    message_manager.assert_answered(callback_id)
    second_message = message_manager.one_message()
    assert second_message.text == "Subdialog"

    # close subdialog
    message_manager.reset_history()
    callback_id = await client.click(
        second_message, InlineButtonTextLocator("Cancel"),
    )
    message_manager.assert_answered(callback_id)
    last_message = message_manager.one_message()
    assert last_message.text == "First"
    assert last_message.reply_markup
