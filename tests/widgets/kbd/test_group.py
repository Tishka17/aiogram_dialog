from unittest.mock import AsyncMock

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
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const


@pytest.mark.asyncio
async def test_render_group(mock_manager) -> None:
    group = Group(
        Button(Const("1"), id="first"),
        Button(Const("2"), id="second"),
        Button(Const("3"), id="third"),
    )

    keyboard = await group.render_keyboard(data={}, manager=mock_manager)

    assert len(keyboard) == 3

    assert len(keyboard[0]) == 1
    assert keyboard[0][0].text == "1"

    assert len(keyboard[1]) == 1
    assert keyboard[1][0].text == "2"

    assert len(keyboard[2]) == 1
    assert keyboard[2][0].text == "3"


@pytest.mark.asyncio
async def test_render_group_with_width(mock_manager) -> None:
    group = Group(
        Button(Const("1"), id="first"),
        Button(Const("2"), id="second"),
        Button(Const("3"), id="third"),
        Button(Const("4"), id="fourth"),
        Button(Const("5"), id="fifth"),
        width=3,
    )

    keyboard = await group.render_keyboard(data={}, manager=mock_manager)

    assert len(keyboard) == 2

    assert len(keyboard[0]) == 3
    assert keyboard[0][0].text == "1"
    assert keyboard[0][1].text == "2"
    assert keyboard[0][2].text == "3"

    assert len(keyboard[1]) == 2
    assert keyboard[1][0].text == "4"
    assert keyboard[1][1].text == "5"


class MainSG(StatesGroup):
    start = State()


on_click_first_button = AsyncMock()
on_click_third_button = AsyncMock()


dialog = Dialog(
    Window(
        Const("stub"),
        Group(
            Button(Const("1"), id="first", on_click=on_click_first_button),
            Button(Const("2"), id="second"),
            Button(Const("3"), id="third", on_click=on_click_third_button),
        ),
        state=MainSG.start,
    ),
)


async def start(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_click_buttons_in_group() -> None:
    dp = Dispatcher()
    dp.include_router(dialog)
    dp.message.register(start, CommandStart())

    client = BotClient(dp)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    # start
    await client.send("/start")
    message = message_manager.one_message()

    # click first button
    await client.click(
        message, InlineButtonTextLocator("1"),
    )
    on_click_first_button.assert_called_once()

    # click third button
    await client.click(
        message, InlineButtonTextLocator("3"),
    )
    on_click_third_button.assert_called_once()
