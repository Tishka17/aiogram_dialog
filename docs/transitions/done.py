from typing import Any

from aiogram.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery

from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Start
from aiogram_dialog.widgets.text import Const


class DialogSG(StatesGroup):
    first = State()


class SubDialogSG(StatesGroup):
    first = State()


async def main_process_result(start_data: Data, result: Any,
                              dialog_manager: DialogManager):
    print("We have result:", result)


dialog = Dialog(
    Window(
        Const("Main dialog"),
        Start(Const("Start 1"), id="start", state=SubDialogSG.first),
        state=DialogSG.first,
    ),
    on_process_result=main_process_result,
)


async def close_subdialog(callback: CallbackQuery, button: Button,
                          manager: DialogManager):
    await manager.done(result={"name": "Tishka17"})


subdialog = Dialog(
    Window(
        Const("Subdialog"),
        Button(Const("Close"), id="btn", on_click=close_subdialog),
        Cancel(Const("Close")),
        state=SubDialogSG.first,
    ),
)
