from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const


class MySG(StatesGroup):
    main = State()


dialog = Dialog(
    Window(
        Const("Hello, unknown person"),
        Button(Const("Useless button"), id="nothing"),
        MySG.main,
    )
)
