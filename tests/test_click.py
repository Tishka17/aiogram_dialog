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


dialog = Dialog(
    Window(
        Format("stub"),
        Button(Const("Button"), id="hello", on_click=on_click),
        state=MainSG.start,
    ),
    Window(
        Format("next"),
        state=MainSG.next,
    )
)


@pytest.mark.asyncio
async def test_click():
    usecase = Mock()
    dp = Dispatcher(usecase=usecase, storage=MemoryStorage())
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

    message_manager.reset_history()

    await client.click(first_message, pattern="Button")
    usecase.assert_called()
    second_message = message_manager.sent_messages[-1]
    assert second_message.text == "next"
    assert not second_message.reply_markup.inline_keyboard