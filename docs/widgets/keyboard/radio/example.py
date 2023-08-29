import operator

from aiogram_dialog.widgets.kbd import Radio
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


fruits_kbd = Radio(
    Format("🔘 {item[0]}"),  # E.g `🔘 Apple`
    Format("⚪️ {item[0]}"),
    id="r_fruits",
    item_id_getter=operator.itemgetter(1),
    items="fruits",
)
