from typing import Any, Dict

from magic_filter import F

from aiogram.filters.state import StatesGroup, State

from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.text import Const, Format, Case

class MySG(StatesGroup):
    window1 = State()
    window2 = State()

# let's assume this is our window data getter
async def get_data(**kwargs):
    return {"color": "red", "number": 42}


# Using string selector as a `selector`.
# The value of data["color"] will be used to select wich option of ``Case`` widget to show.
#
# `text` will produce text `Square`
text = Case(
    {
        "red": Const("Square"),
        "green": Const("Unicorn"),
        "blue": Const("Moon"),
        ...: Const("Unknown creature"),
    },
    selector="color",
)


# Using function as a `selector`.
# The result of this function will be used to select wich option of ``Case`` widget to show.
#
# `text2` will produce text `42 is even!`
def parity_selector(data: Dict, case: Case, manager: DialogManager):
    return data["number"] % 2


text2 = Case(
    {
        0: Format("{number} is even!"),
        1: Const("It is Odd"),
    },
    selector=parity_selector,
)


# Using F-filters as a selector.
# The value of data["dialog_data"]["user"]["test_result"] will be used to select wich option
# of ``Case`` widget to show.
#
# `text3` will produce text `Great job!`
text3 = Case(
    {
        True: Const("Great job!"),
        False: Const("Try again.."),
    },
    selector=F["dialog_data"]["user"]["test_result"],
)


async def on_dialog_start(start_data: Any, manager: DialogManager):
    manager.dialog_data['user'] = {
        'test_result': True,
    }


dialog = Dialog(
    Window(
        text,
        text2,
        text3,
        state=MySG.window1,
        getter=get_data
    ),
    on_start=on_dialog_start
)