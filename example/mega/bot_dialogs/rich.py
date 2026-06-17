from aiogram.enums import ParseMode

from aiogram_dialog import Dialog, Window
from aiogram_dialog.api.entities import RichParseMode
from aiogram_dialog.widgets.rich import Rich
from aiogram_dialog.widgets.text import Const
from . import states
from .common import MAIN_MENU_BUTTON

rich_dialog = Dialog(
    Window(
        Const("<h1>This is rich text header</h1>"),
        Const("<img src=\"https://telegram.org/example/photo.jpg\" />"),
        Const("<p>Press <b>Main menu</b> to return</p>"),
        MAIN_MENU_BUTTON,
        rich=Rich(
            parse_mode=RichParseMode.html,
        ),
        state=states.Rich.MAIN,
    )
)