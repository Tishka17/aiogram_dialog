from aiogram import Dispatcher
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, DialogRegistry, Window
from aiogram_dialog.widgets.text import Format


class MainSG(StatesGroup):
    start = State()


def test_register():
    registry = DialogRegistry()
    dialog = Dialog(
        Window(
            Format("stub"),
            state=MainSG.start,
        ),
    )
    registry.register(dialog)

    dp = Dispatcher()
    registry.setup(dp)
