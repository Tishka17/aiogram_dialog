from datetime import datetime
from typing import Optional
from unittest.mock import Mock

import pytest
from aiogram import Dispatcher, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, Update, Chat, User, CallbackQuery

from aiogram_dialog import Dialog, Window, DialogRegistry, DialogManager
from aiogram_dialog.api.entities import NewMessage
from aiogram_dialog.api.protocols import MessageManagerProtocol
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

TEST_CHAT = Chat(id=1, type="")
TEST_USER = User(id=1, is_bot=False, first_name="")


class MockMessageManager(MessageManagerProtocol):
    def __init__(self):
        self.last_message: Optional[NewMessage] = None

    async def remove_kbd(self, bot: Bot, old_message: Optional[Message]):
        pass

    async def show_message(self, bot: Bot, new_message: NewMessage,
                           old_message: Optional[Message]):
        self.last_message = new_message
        return Message(
            message_id=1,
            text="fake",
            date=datetime.now(),
            chat=new_message.chat,
        )


class FakeBot(Bot):
    def __init__(self):
        pass

    @property
    def id(self):
        return 1

    async def __call__(self, *args, **kwargs):
        pass  # TODO Remove, move callback.answer() to message manager


@pytest.mark.asyncio
async def test_click():
    usecase = Mock()
    bot = FakeBot()
    dp = Dispatcher(usecase=usecase, storage=MemoryStorage())
    message_manager = MockMessageManager()
    registry = DialogRegistry(dp, message_manager=message_manager)
    registry.register_start_handler(MainSG.start)
    registry.register(dialog)

    await dp.feed_update(bot=bot, update=Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.fromtimestamp(1234567890),
            chat=TEST_CHAT,
            from_user=TEST_USER,
            text="/start",
        )
    ))

    first_message = message_manager.last_message
    assert first_message
    assert first_message.text == "stub"
    assert first_message.reply_markup
    first_keyboard = first_message.reply_markup.inline_keyboard
    print(first_keyboard)

    await dp.feed_update(bot=bot, update=Update(
        update_id=2,
        callback_query=CallbackQuery(
            id=1,
            data=first_keyboard[0][0].callback_data,
            chat_instance="--",
            from_user=TEST_USER,
            message=Message(
                message_id=1,
                text="fake",
                date=datetime.now(),
                chat=TEST_CHAT,
            ),
        ),
    ))

    usecase.assert_called()
    second_message = message_manager.last_message
    assert second_message
    assert second_message.text == "next"
    assert not second_message.reply_markup.inline_keyboard
