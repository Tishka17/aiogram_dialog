from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format


class MySG(StatesGroup):
    main = State()


async def get_data(**kwargs):
    return {
        "name": "Tishka17",
    }


dialog = Dialog(
    Window(
        Format("Hello, {name}!"),
        Button(Const("Useless button"), id="nothing"),
        state=MySG.main,
        getter=get_data,  # here we set our data getter
    )
)
