from aiogram import Dispatcher
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, setup_dialogs, Window
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
