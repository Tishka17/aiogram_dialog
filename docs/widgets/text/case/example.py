from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Case, Const, Format


# let's assume this is our window data getter
async def get_data(**kwargs):
    return {"color": "red", "number": 42}


# This will produce text `Square`
text = Case(
    {
        "red": Const("Square"),
        "green": Const("Unicorn"),
        "blue": Const("Moon"),
        ...: Const("Unknown creature"),
    },
    selector="color",
)


# This one will produce text `42 is even!`
def parity_selector(data: Dict, case: Case, manager: DialogManager):
    return data["number"] % 2


text2 = Case(
    {
        0: Format("{number} is even!"),
        1: Const("It is Odd"),
    },
    selector=parity_selector,
)
