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
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.widgets.kbd import Button, Group, ScrollingGroup
from aiogram_dialog.widgets.text import Const


def _texts(keyboard) -> list[list[str]]:
    return [[button.text for button in row] for row in keyboard]


def _buttons(texts: list[str]) -> list[Button]:
    return [
        Button(Const(text), id=f"b{idx}")
        for idx, text in enumerate(texts)
    ]


async def _rendered_rows(keyboard) -> list[list[str]]:
    """Render a keyboard widget through the public dialog path.

    Returns rows as lists of button texts, so tests assert real layout
    instead of reaching into private wrapping methods.
    """
    class RenderSG(StatesGroup):
        start = State()

    async def start_dialog(event: Any, dialog_manager: DialogManager) -> None:
        await dialog_manager.start(RenderSG.start, mode=StartMode.RESET_STACK)

    window = Window(Const("stub"), keyboard, state=RenderSG.start)
    message_manager = MockMessageManager()
    dp = Dispatcher(storage=JsonMemoryStorage())
    dp.include_router(Dialog(window))
    setup_dialogs(dp, message_manager=message_manager)
    dp.message.register(start_dialog, CommandStart())
    client = BotClient(dp, chat_id=-1, user_id=1, chat_type="group")

    await client.send("/start")
    message = message_manager.one_message()
    return _texts(message.reply_markup.inline_keyboard)


def test_both_width_and_symbols_raises():
    with pytest.raises(ValueError, match="Only one of"):
        Group(width=2, width_symbols=4)


def test_scrolling_group_both_raises():
    with pytest.raises(ValueError, match="Only one of"):
        ScrollingGroup(id="s", width=2, width_symbols=4)


def test_only_symbols_stored():
    group = Group(width_symbols=4)
    assert group.width_symbols == 4
    assert group.width is None


def test_only_width_stored():
    group = Group(width=2)
    assert group.width == 2
    assert group.width_symbols is None


@pytest.mark.asyncio
async def test_symbols_basic_packing():
    group = Group(*_buttons(["ab", "cd", "ef", "ghijkl"]), width_symbols=4)
    assert await _rendered_rows(group) == [["ab", "cd"], ["ef"], ["ghijkl"]]


@pytest.mark.asyncio
async def test_symbols_exact_boundary_stays_in_row():
    group = Group(*_buttons(["ab", "cd"]), width_symbols=4)
    assert await _rendered_rows(group) == [["ab", "cd"]]


@pytest.mark.asyncio
async def test_symbols_single_button_longer_than_limit():
    group = Group(*_buttons(["xxxxxx"]), width_symbols=3)
    assert await _rendered_rows(group) == [["xxxxxx"]]


@pytest.mark.asyncio
async def test_scrolling_group_symbols_wraps():
    group = ScrollingGroup(
        *_buttons(["ab", "cd", "ef"]),
        id="s",
        width_symbols=4,
        height=10,
        hide_pager=True,
    )
    assert await _rendered_rows(group) == [["ab", "cd"], ["ef"]]
