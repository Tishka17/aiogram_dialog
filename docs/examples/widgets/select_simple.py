import operator

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


check = Select(
    Format("✓ {item[0]} ({pos}/{data[count]})"),  # E.g `✓ Apple (1/4)`
    Format("{item[0]} ({pos}/{data[count]})"),
    id="check",
    item_id_getter=operator.itemgetter(1),  # each item is a tuple with id on a first position
    items="fruits",  # we will use items from window data at a key `fruits`
    multiple=True,  # enable multiple items selection
)
