from typing import Any
from unittest.mock import Mock

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
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format


class MainSG(StatesGroup):
    start = State()
    next = State()


async def on_click(event, button, manager: DialogManager) -> None:
    manager.middleware_data["usecase"]()
    await manager.next()


async def on_finish(event, button, manager: DialogManager) -> None:
    await manager.done()


async def second_getter(user_getter, **kwargs) -> dict[str, Any]:
    return {
        "user": user_getter(),
    }


dialog = Dialog(
    Window(
        Format("stub"),
        Button(Const("Button"), id="hello", on_click=on_click),
        state=MainSG.start,
    ),
    Window(
        Format("Next {user}"),
        Button(Const("Finish"), id="hello", on_click=on_finish),
        state=MainSG.next,
        getter=second_getter,
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_click():
    usecase = Mock()
    user_getter = Mock(side_effect=["Username"])
    dp = Dispatcher(
        usecase=usecase, user_getter=user_getter,
        storage=JsonMemoryStorage(),
    )
    dp.include_router(dialog)
    dp.message.register(start, CommandStart())

    client = BotClient(dp)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    # start
    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.text == "stub"
    assert first_message.reply_markup
    user_getter.assert_not_called()

    # redraw
    message_manager.reset_history()
    await client.send("whatever")

    first_message = message_manager.one_message()
    assert first_message.text == "stub"

    # click next
    message_manager.reset_history()
    callback_id = await client.click(
        first_message, InlineButtonTextLocator("Button"),
    )

    message_manager.assert_answered(callback_id)
    usecase.assert_called()
    second_message = message_manager.one_message()
    assert second_message.text == "Next Username"
    assert second_message.reply_markup.inline_keyboard
    user_getter.assert_called_once()
