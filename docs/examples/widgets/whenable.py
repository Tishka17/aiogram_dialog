from typing import Dict

from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Row, Group
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.when import Whenable


class MySG(StatesGroup):
    main = State()


async def get_data(**kwargs):
    return {
        "name": "Tishka17",
        "extended": False,
    }


def is_tishka17(data: Dict, widget: Whenable, manager: DialogManager):
    return data.get("name") == "Tishka17"


window = Window(
    Multi(
        Const("Hello"),
        Format("{name}", when="extended"),
        sep=" "
    ),
    Group(
        Row(
            Button(Const("Wait"), id="wait"),
            Button(Const("Ignore"), id="ignore"),
            when="extended",
        ),
        Button(Const("Admin mode"), id="nothing", when=is_tishka17),
    ),
    MySG.main,
    getter=get_data,
)
