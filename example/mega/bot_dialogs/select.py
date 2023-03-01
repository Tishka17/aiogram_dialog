from aiogram_dialog import (
    Dialog, Window, )
from aiogram_dialog.widgets.kbd import (
    SwitchTo, Select, Column, Radio, Multiselect,
)
from aiogram_dialog.widgets.text import Const, Format
from . import states
from .common import MAIN_MENU_BUTTON

Selects_MAIN_MENU_BUTTON = SwitchTo(
    text=Const("Back"), id="back", state=states.Selects.MAIN,
)

FRUITS_KEY = "fruits"


async def getter(**_kwargs):
    return {
        FRUITS_KEY: ["Apple", "Banana", "Orange", "Pear"],
    }


def fruit_id_getter(fruit):
    return fruit


menu_window = Window(
    Const("Different keyboard Selects."),
    SwitchTo(
        text=Const("Select"),
        id="row",
        state=states.Selects.SELECT,
    ),
    SwitchTo(
        text=Const("Radio"),
        id="column",
        state=states.Selects.RADIO,
    ),
    SwitchTo(
        text=Const("Multiselect"),
        id="group",
        state=states.Selects.MULTI,
    ),
    MAIN_MENU_BUTTON,
    state=states.Selects.MAIN,
)
select_window = Window(
    Const("Select widget"),
    Column(
        Select(
            text=Format("{item}"),
            id="sel",
            items=FRUITS_KEY,
            item_id_getter=fruit_id_getter,
        )
    ),
    Selects_MAIN_MENU_BUTTON,
    state=states.Selects.SELECT,
    getter=getter,
)
radio_window = Window(
    Const("Radio widget"),

    Column(
        Radio(
            checked_text=Format("🔘 {item}"),
            unchecked_text=Format("⚪️ {item}"),
            id="radio",
            items=FRUITS_KEY,
            item_id_getter=fruit_id_getter,
        )
    ),
    Selects_MAIN_MENU_BUTTON,
    state=states.Selects.RADIO,
    getter=getter,
)
multiselect_window = Window(
    Const("Multiselect widget"),

    Column(
        Multiselect(
            checked_text=Format("✓ {item}"),
            unchecked_text=Format("{item}"),
            id="multi",
            items=FRUITS_KEY,
            item_id_getter=fruit_id_getter,
        )
    ),
    Selects_MAIN_MENU_BUTTON,
    state=states.Selects.MULTI,
    getter=getter,
)
selects_dialog = Dialog(
    menu_window,
    select_window,
    radio_window,
    multiselect_window,
)
