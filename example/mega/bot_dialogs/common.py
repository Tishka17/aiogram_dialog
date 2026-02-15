from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Const
from . import states

MAIN_MENU_BUTTON = Start(
    text=Const("☰ Main menu"),
    id="__main__",
    state=states.Main.MAIN,
    style=Style(style="primary"),
)
