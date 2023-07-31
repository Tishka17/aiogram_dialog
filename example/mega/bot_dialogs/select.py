from dataclasses import dataclass
from typing import Any

from aiogram.types import CallbackQuery
from magic_filter import F

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    SwitchTo, Select, Column, Radio, Multiselect,
)
from aiogram_dialog.widgets.text import Const, Format, List
from . import states
from .common import MAIN_MENU_BUTTON

Selects_MAIN_MENU_BUTTON = SwitchTo(
    text=Const("Back"), id="back", state=states.Selects.MAIN,
)

FRUITS_KEY = "fruits"
OTHER_KEY = "others"


@dataclass
class Fruit:
    id: str
    name: str


async def getter(**_kwargs):
    return {
        FRUITS_KEY: [
            Fruit("apple_a", "Apple"),
            Fruit("banana_b", "Banana"),
            Fruit("orange_o", "Orange"),
            Fruit("pear_p", "Pear"),
        ],
        OTHER_KEY: {
            FRUITS_KEY: [
                Fruit("mango_m", "Mango"),
                Fruit("papaya_p", "Papaya"),
                Fruit("kiwi_k", "Kiwi"),
            ],
        }
    }


def fruit_id_getter(fruit: Fruit) -> str:
    return fruit.id


async def on_item_selected(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        selected_item: str,
):
    await callback.answer(selected_item)


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
    List(
        field=Format("+ {item.name} - {item.id}"),
        items=FRUITS_KEY
        # Alternatives:
            #items=lambda d: d[OTHER_KEY][FRUITS_KEY],
            #items=F[OTHER_KEY][FRUITS_KEY],
    ),
    Column(
        Select(
            text=Format("{item.name} ({item.id})"),
            id="sel",
            items=FRUITS_KEY,
            # Alternatives:
                #items=lambda d: d[OTHER_KEY][FRUITS_KEY],
                #items=F[OTHER_KEY][FRUITS_KEY],
            item_id_getter=fruit_id_getter,
            on_click=on_item_selected,
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
            checked_text=Format("🔘 {item.name}"),
            unchecked_text=Format("⚪️ {item.name}"),
            id="radio",
            items=FRUITS_KEY,
            # Alternatives:
                #items=lambda d: d[OTHER_KEY][FRUITS_KEY],
                #items=F[OTHER_KEY][FRUITS_KEY],
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
            checked_text=Format("✓ {item.name}"),
            unchecked_text=Format("{item.name}"),
            id="multi",
            items=FRUITS_KEY,
            # Alternatives:
                #items=lambda d: d[OTHER_KEY][FRUITS_KEY],
                #items=F[OTHER_KEY][FRUITS_KEY],
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
