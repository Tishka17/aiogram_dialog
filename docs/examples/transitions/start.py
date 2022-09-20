from aiogram.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const


class DialogSG(StatesGroup):
    first = State()


class SubDialogSG(StatesGroup):
    first = State()
    second = State()


async def start_subdialog(callback: CallbackQuery, button: Button,
                          manager: DialogManager):
    await manager.start(SubDialogSG.second, data={"key": "value"})


dialog = Dialog(
    Window(
        Const("Main dialog"),
        Start(Const("Start 1"), id="start", state=SubDialogSG.first),
        Button(Const("Start 2"), id="sec", on_click=start_subdialog),
        state=DialogSG.first,
    ),
)

subdialog = Dialog(
    Window(
        Const("Subdialog: first"),
        state=SubDialogSG.first,
    ),
    Window(
        Const("Subdialog: second"),
        state=SubDialogSG.second,
    ),
)
