from typing import Any
import operator

from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Format


# let's assume this is our window data getter
async def get_data(**kwargs):
    fruits = [
        ("Apple", '1'),
        ("Pear", '2'),
        ("Orange", '3'),
        ("Banana", '4'),
    ]
    return {
        "fruits": fruits,
        "count": len(fruits),
    }


async def on_fruit_selected(callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    print("Fruit selected: ", item_id)


fruits_kbd = Select(
    Format("{item[0]} ({pos}/{data[count]})"),  # E.g `✓ Apple (1/4)`
    id="s_fruits",
    item_id_getter=operator.itemgetter(1),  # each item is a tuple with id on a first position
    items="fruits",  # we will use items from window data at a key `fruits`
    on_click=on_fruit_selected,
)
