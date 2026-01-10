from unittest.mock import Mock

import pytest
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from jinja2 import UndefinedError

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Jinja


class MainSG(StatesGroup):
    start = State()



dialog = Dialog(
    Window(
        Const("stub"),
        ScrollingGroup(
            Select(
                Jinja("{{undefined + 1}}"),
                id="select_id",
                item_id_getter=lambda x: x,
                items="data",
            ),
            id="scrolling_group_id",
            width=1,
            height=10,
        ),
        state=MainSG.start,
        getter={"data": [{"foo": 1}]},
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_exception_notes():
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

    with pytest.raises(UndefinedError) as exc_info:
        await client.send("/start")
    assert exc_info.value.__notes__
    assert Jinja.__name__ in exc_info.value.__notes__[0]
    assert exc_info.value.__notes__[1:] == [
        "at <Select id=select_id>",
        "at <ScrollingGroup id=scrolling_group_id>",
        "aiogram-dialog state: <State 'MainSG:start'>",
    ]
