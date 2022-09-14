from aiogram.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const


class DialogSG(StatesGroup):
    first = State()
    second = State()
    third = State()


async def to_second(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(DialogSG.second)


async def go_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.back()


async def go_next(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.next()


dialog = Dialog(
    Window(
        Const("First"),
        Button(Const("To second"), id="sec", on_click=to_second),
        state=DialogSG.first,
    ),
    Window(
        Const("Second"),
        Row(
            Button(Const("Back"), id="back2", on_click=go_back),
            Button(Const("Next"), id="next2", on_click=go_next),
        ),
        state=DialogSG.second,
    ),
    Window(
        Const("Third"),
        Button(Const("Back"), id="back3", on_click=go_back),
        state=DialogSG.third,
    )
)
