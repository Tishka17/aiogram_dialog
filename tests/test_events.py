from typing import Any

import pytest
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ChatMemberMember, ChatMemberOwner

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.widgets.text import Format


class MainSG(StatesGroup):
    start = State()


window = Window(
    Format("stub"),
    state=MainSG.start,
)


async def start(event: Any, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


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
    return BotClient(dp)


@pytest.mark.asyncio
async def test_click(dp, client, message_manager):
    dp.message.register(start, CommandStart())
    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.text == "stub"


@pytest.mark.asyncio
async def test_request_join(dp, client, message_manager):
    dp.chat_join_request.register(start)
    await client.request_chat_join()
    first_message = message_manager.one_message()
    assert first_message.text == "stub"


@pytest.mark.asyncio
async def test_my_chat_member_update(dp, client, message_manager):
    dp.my_chat_member.register(start)
    await client.my_chat_member_update(
        ChatMemberMember(user=client.user),
        ChatMemberOwner(user=client.user, is_anonymous=False),
    )
    first_message = message_manager.one_message()
    assert first_message.text == "stub"
