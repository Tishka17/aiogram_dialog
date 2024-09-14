from aiogram import F
from aiogram.filters.state import State, StatesGroup
from aiogram_dialog import (
    Window,
    Dialog,
)
from aiogram_dialog.widgets.kbd import (
    Url,
    ListGroup,
    SwitchTo,
    Back,
)
from aiogram_dialog.widgets.text import Const, Format


class SG(StatesGroup):
    main = State()
    result = State()


success = F["products"]
fail = ~success


async def actions(**kwargs):
    products = [
        {"id": 1, "name": "Ferrari", "category": "car",
         "url": "https://www.ferrari.com/"},
        {"id": 2, "name": "Detroit", "category": "game",
         "url": "https://wikipedia.org/wiki/Detroit:_Become_Human"},
    ]
    return {
        "products": products,
    }


dialog = Dialog(
    Window(
        Const("Click find products to show a list of available products:"),
        SwitchTo(Const("Find products"), id="search", state=SG.result),
        state=SG.main,
    ),
    Window(
        Const("Searching results:", when=success),
        Const("Search did not return any results", when=fail),
        ListGroup(
            Url(
                Format("{item[name]} ({item[category]})"),
                Format("{item[url]}"),
                id="url",
            ),
            id="select_search",
            item_id_getter=lambda item: item["id"],
            items="products",
        ),
        Back(Const("Back")),
        state=SG.result,
        getter=actions,
    )
)
