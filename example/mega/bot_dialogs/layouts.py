from aiogram_dialog import (
    Dialog, Window,
)
from aiogram_dialog.widgets.kbd import (
    SwitchTo, Select, Button, Row, Column, Group,
)
from aiogram_dialog.widgets.text import Const, Format
from . import states
from .common import MAIN_MENU_BUTTON

LAYOUTS_MAIN_MENU_BUTTON = SwitchTo(
    text=Const("Back"), id="back", state=states.Layouts.MAIN,
)

SELECT = Select(
    text=Format("{item}"),
    id="sel",
    items=["Apple", "Banana", "Orange", "Pear"],
    item_id_getter=lambda x: x,
)
BUTTON = Button(
    text=Const("Additional button"),
    id="btn",
)

menu_window = Window(
    Const("Different keyboard layouts."),
    SwitchTo(
        text=Const("↔️ Row"),
        id="row",
        state=states.Layouts.ROW,
    ),
    SwitchTo(
        text=Const("↕️ Column"),
        id="column",
        state=states.Layouts.COLUMN,
    ),
    SwitchTo(
        text=Const("↩️ Group"),
        id="group",
        state=states.Layouts.GROUP,
    ),
    MAIN_MENU_BUTTON,
    state=states.Layouts.MAIN,
)
row_window = Window(
    Const("Select and Button inside `Row`"),
    Row(
        SELECT,
        BUTTON,
    ),
    LAYOUTS_MAIN_MENU_BUTTON,
    state=states.Layouts.ROW,
)
column_window = Window(
    Const("Select and Button inside `Column`"),
    Column(
        SELECT,
        BUTTON,
    ),
    LAYOUTS_MAIN_MENU_BUTTON,
    state=states.Layouts.COLUMN,
)
group_window = Window(
    Const("Select and Button inside `Group` with width=2"),
    Group(
        SELECT,
        BUTTON,
        width=2,
    ),
    LAYOUTS_MAIN_MENU_BUTTON,
    state=states.Layouts.GROUP,
)
layouts_dialog = Dialog(
    row_window,
    column_window,
    group_window,
    menu_window,
)
