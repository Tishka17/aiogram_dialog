from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, SwitchTo, Next, Back
from aiogram_dialog.widgets.text import Const


class DialogSG(StatesGroup):
    first = State()
    second = State()
    third = State()


dialog = Dialog(
    Window(
        Const("First"),
        SwitchTo(Const("To second"), id="sec", state=DialogSG.second),
        state=DialogSG.first,
    ),
    Window(
        Const("Second"),
        Row(
            Back(),
            Next(),
        ),
        state=DialogSG.second,
    ),
    Window(
        Const("Third"),
        Back(),
        state=DialogSG.third,
    )
)
