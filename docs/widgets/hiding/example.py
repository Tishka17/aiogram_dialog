from aiogram.filters.state import State, StatesGroup
from magic_filter import F

from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const, Format, Multi


class MySG(StatesGroup):
    main = State()


async def get_data(**kwargs):
    return {
        "name": "Tishka17",
        "extended": False,
    }


def is_tishka17(data: dict, widget: Whenable, manager: DialogManager):
    return data.get("name") == "Tishka17"


window = Window(
    Multi(
        Const("Hello"),
        Format("{name}", when="extended"),
        sep=" ",
    ),
    Group(
        Row(
            Button(Const("Wait"), id="wait"),
            Button(Const("Ignore"), id="ignore"),
            when=F["extended"],
        ),
        Button(Const("Admin mode"), id="nothing", when=is_tishka17),
    ),
    state=MySG.main,
    getter=get_data,
)
