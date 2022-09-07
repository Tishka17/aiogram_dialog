from aiogram import Dispatcher
from aiogram.fsm.state import StatesGroup, State

from aiogram_dialog import Dialog, Window, DialogRegistry
from aiogram_dialog.widgets.text import Format


class MainSG(StatesGroup):
    start = State()


dialog = Dialog(
    Window(
        Format("stub"),
        state=MainSG.start,
    )
)


def test_register():
    dp = Dispatcher()
    registry = DialogRegistry(dp)
    registry.register(dialog)
