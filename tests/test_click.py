from typing import Any, Dict
from unittest.mock import Mock

import pytest
from aiogram import Dispatcher
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram_dialog import Dialog, Window, DialogRegistry, DialogManager
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const


class MainSG(StatesGroup):
    start = State()
    next = State()


async def on_click(event, button, manager: DialogManager) -> None:
    manager.middleware_data["usecase"]()
    await manager.next()


async def second_getter(user_getter, **kwargs) -> Dict[str, Any]:
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
        state=MainSG.next,
        getter=second_getter,
    )
)


@pytest.mark.asyncio
async def test_click():
    usecase = Mock()
    user_getter = Mock(side_effect=["Username"])
    dp = Dispatcher(
        usecase=usecase, user_getter=user_getter,
        storage=MemoryStorage(),
    )
    client = BotClient(dp)
    message_manager = MockMessageManager()
    registry = DialogRegistry(dp, message_manager=message_manager)
    registry.register_start_handler(MainSG.start)
    registry.register(dialog)

    await client.send("/start")
    assert len(message_manager.sent_messages) == 1
    first_message = message_manager.sent_messages[-1]
    assert first_message.text == "stub"
    assert first_message.reply_markup
    user_getter.assert_not_called()

    message_manager.reset_history()
    await client.send("whatever")

    assert len(message_manager.sent_messages) == 1
    first_message = message_manager.sent_messages[-1]
    assert first_message.text == "stub"

    message_manager.reset_history()
    await client.click(first_message, pattern="Button")

    usecase.assert_called()
    second_message = message_manager.sent_messages[-1]
    assert second_message.text == "Next Username"
    assert not second_message.reply_markup.inline_keyboard
    user_getter.assert_called_once()
