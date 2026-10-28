from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, SwitchTo
from aiogram_dialog.widgets.rich import RichBlocks, RichHtml, RichMarkdown
from aiogram_dialog.widgets.text import Const
from . import states
from .common import MAIN_MENU_BUTTON

FORMATS = Row(
    SwitchTo(Const("HTML"), id="html", state=states.Rich.MAIN),
    SwitchTo(Const("Markdown"), id="markdown", state=states.Rich.MARKDOWN),
    SwitchTo(Const("Blocks"), id="blocks", state=states.Rich.BLOCKS),
)

rich_dialog = Dialog(
    Window(
        Const("<h1>This is rich text header</h1>"),
        Const('<img src="https://telegram.org/example/photo.jpg"/>'),
        Const("<p>Buttons below are a part of the <b>HTML</b> message</p>"),
        FORMATS,
        MAIN_MENU_BUTTON,
        rich=RichHtml(),
        state=states.Rich.MAIN,
    ),
    Window(
        Const(
            "# This is rich text header\n\n"
            "![](https://telegram.org/example/photo.jpg)\n\n"
            "Buttons below are a part of the **Markdown** message",
        ),
        FORMATS,
        MAIN_MENU_BUTTON,
        rich=RichMarkdown(),
        state=states.Rich.MARKDOWN,
    ),
    Window(
        Const("Buttons below are a part of the message built from blocks"),
        FORMATS,
        MAIN_MENU_BUTTON,
        rich=RichBlocks(),
        state=states.Rich.BLOCKS,
    ),
)
