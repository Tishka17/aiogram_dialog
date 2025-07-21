# tests for https://github.com/Tishka17/aiogram_dialog/issues/493

import pytest
from aiogram import Dispatcher
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, setup_dialogs
from aiogram_dialog.widgets.text import Const


class First(StatesGroup):
    state = State()


class Second(StatesGroup):
    state = State()


@pytest.mark.asyncio
async def test_one_state_group_per_dialog() -> None:
    first_dialog = Dialog(Window(Const("foo"), state=First.state))
    second_dialog = Dialog(Window(Const("bar"), state=First.state))
    dp = Dispatcher()
    dp.include_routers(first_dialog, second_dialog)

    setup_dialogs(dp)
    with pytest.raises(
        ValueError,
        match=r"StatesGroup '.+' is used in multiple dialogs: '.+' and '.+'",
    ):
        await dp.emit_startup()


def test_one_state_per_window() -> None:
    first_window = Window(Const("foo"), state=First.state)
    seconds_window = Window(Const("bar"), state=First.state)

    with pytest.raises(ValueError, match="Multiple windows with state"):
        Dialog(first_window, seconds_window)


def test_one_state_group_in_one_dialog() -> None:
    first_window = Window(Const("foo"), state=First.state)
    seconds_window = Window(Const("bar"), state=Second.state)

    with pytest.raises(
        ValueError,
        match="All windows must be attached to same StatesGroup",
    ):
        Dialog(first_window, seconds_window)
