from aiogram.enums import ParseMode

from aiogram_dialog import Dialog
from aiogram_dialog.api.internal.render import RenderMode
from aiogram_dialog.rich_window import RichWindow
from aiogram_dialog.widgets.rich.button import Button
from aiogram_dialog.widgets.rich.text import Const
from . import states
from .common import MAIN_MENU_BUTTON

rich_dialog = Dialog(
    RichWindow(
        Const("<h1>This is rich text header</h1>"),
        Button(Const("111")),
        render_mode=RenderMode.RICH_HTML,
        state=states.Rich.MAIN,
    )
)
