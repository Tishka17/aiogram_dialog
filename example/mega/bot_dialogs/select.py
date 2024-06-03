from dataclasses import dataclass
from typing import Any

from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Column, Multiselect, Radio,
    Select, SwitchTo, Toggle,
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
    emoji: str


async def getter(**_kwargs):
    return {
        FRUITS_KEY: [
            Fruit("apple_a", "Apple", "🍏"),
            Fruit("banana_b", "Banana", "🍌"),
            Fruit("orange_o", "Orange", "🍊"),
            Fruit("pear_p", "Pear", "🍐"),
        ],
        OTHER_KEY: {
            FRUITS_KEY: [
                Fruit("mango_m", "Mango", "🥭"),
                Fruit("pineapple_p", "Pineapple", "🍍"),
                Fruit("kiwi_k", "Kiwi", "🥝"),
            ],
        },
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
        id="s_select",
        state=states.Selects.SELECT,
    ),
    SwitchTo(
        text=Const("Radio"),
        id="s_radio",
        state=states.Selects.RADIO,
    ),
    SwitchTo(
        text=Const("Multiselect"),
        id="s_multi",
        state=states.Selects.MULTI,
    ),
    SwitchTo(
        text=Const("Toggle"),
        id="s_toggle",
        state=states.Selects.TOGGLE,
    ),
    MAIN_MENU_BUTTON,
    state=states.Selects.MAIN,
)
select_window = Window(
    Const("Select widget"),
    List(
        field=Format("+ {item.emoji} {item.name} - {item.id}"),
        items=FRUITS_KEY,
        # Alternatives:
        # items=lambda d: d[OTHER_KEY][FRUITS_KEY],  # noqa: E800
        # items=F[OTHER_KEY][FRUITS_KEY],  # noqa: E800
    ),
    Column(
        Select(
            text=Format("{item.emoji} {item.name} ({item.id})"),
            id="sel",
            items=FRUITS_KEY,
            # Alternatives:
            # items=lambda d: d[OTHER_KEY][FRUITS_KEY],  # noqa: E800
            # items=F[OTHER_KEY][FRUITS_KEY],  # noqa: E800
            item_id_getter=fruit_id_getter,
            on_click=on_item_selected,
        ),
    ),
    Selects_MAIN_MENU_BUTTON,
    state=states.Selects.SELECT,
    getter=getter,
    preview_data=getter,
)
radio_window = Window(
    Const("Radio widget"),
    Column(
        Radio(
            checked_text=Format("🔘 {item.emoji} {item.name}"),
            unchecked_text=Format("⚪️ {item.emoji} {item.name}"),
            id="radio",
            items=FRUITS_KEY,
            # Alternatives:
            # items=lambda d: d[OTHER_KEY][FRUITS_KEY],  # noqa: E800
            # items=F[OTHER_KEY][FRUITS_KEY],  # noqa: E800
            item_id_getter=fruit_id_getter,
        ),
    ),
    Selects_MAIN_MENU_BUTTON,
    state=states.Selects.RADIO,
    getter=getter,
    preview_data=getter,
)
multiselect_window = Window(
    Const("Multiselect widget"),

    Column(
        Multiselect(
            checked_text=Format("✓ {item.name}"),
            unchecked_text=Format("{item.emoji} {item.name}"),
            id="multi",
            items=FRUITS_KEY,
            # Alternatives:
            # items=lambda d: d[OTHER_KEY][FRUITS_KEY],  # noqa: E800
            # items=F[OTHER_KEY][FRUITS_KEY],  # noqa: E800
            item_id_getter=fruit_id_getter,
        ),
    ),
    Selects_MAIN_MENU_BUTTON,
    state=states.Selects.MULTI,
    getter=getter,
    preview_data=getter,
)
toggle_window = Window(
    Const("Toggle widget. Click to switch between items."),
    Const("It is compatible and interchangeable with `Radio`."),
    Column(
        Toggle(
            text=Format("{item.emoji} {item.name}"),
            id="radio",
            items=FRUITS_KEY,
            item_id_getter=fruit_id_getter,
        ),
    ),
    Selects_MAIN_MENU_BUTTON,
    state=states.Selects.TOGGLE,
    getter=getter,
    preview_data=getter,
)
selects_dialog = Dialog(
    menu_window,
    select_window,
    radio_window,
    multiselect_window,
    toggle_window,
)
