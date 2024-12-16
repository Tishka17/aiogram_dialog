from aiogram import Dispatcher
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, setup_dialogs
from aiogram_dialog.widgets.text import Format


class MainSG(StatesGroup):
    start = State()


def test_register():
    dialog = Dialog(
        Window(
            Format("stub"),
            state=MainSG.start,
        ),
    )

    dp = Dispatcher()
    dp.include_router(dialog)
    setup_dialogs(dp)


def test_name_state_group():
    dialog = Dialog(
        Window(
            Format("stub"),
            state=MainSG.start,
        ),
    )
    assert dialog.name == "MainSG"


def test_name_explicit():
    dialog = Dialog(
        Window(
            Format("stub"),
            state=MainSG.start,
        ),
        name="FooDialog",
    )
    assert dialog.name == "FooDialog"
