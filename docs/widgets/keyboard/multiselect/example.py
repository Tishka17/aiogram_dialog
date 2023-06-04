import operator

from aiogram_dialog.widgets.kbd import Multiselect
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


fruits_kbd = Multiselect(
    Format("✓ {item[0]}"),  # E.g `✓ Apple`
    Format("{item[0]}"),
    id="m_fruits",
    item_id_getter=operator.itemgetter(1),
    items="fruits",
)
