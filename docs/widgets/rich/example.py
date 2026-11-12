from aiogram.filters.state import State, StatesGroup

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Next
from aiogram_dialog.widgets.rich import RichBlocks, RichHtml, RichMarkdown
from aiogram_dialog.widgets.text import Const, Jinja


class SG(StatesGroup):
    HTML = State()
    MARKDOWN = State()
    BLOCKS = State()


html_window = Window(
    Const("<h1>Rich message</h1>"),
    Jinja("<p>Hello, <b>{{ name }}</b>!</p>"),
    Const('<img src="https://telegram.org/example/photo.jpg"/>'),
    Next(),
    rich=RichHtml(),
    state=SG.HTML,
)

markdown_window = Window(
    Const(
        "# Rich message\n\n"
        "| Metric | Value |\n"
        "|:-------|------:|\n"
        "| Speed  | **42** |",
    ),
    Next(),
    rich=RichMarkdown(),
    state=SG.MARKDOWN,
)

blocks_window = Window(
    Const("This text is sent as is"),
    rich=RichBlocks(),
    state=SG.BLOCKS,
)
