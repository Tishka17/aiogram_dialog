from aiogram.filters.state import State, StatesGroup

from aiogram_dialog import Window
from aiogram_dialog.widgets.link_preview import LinkPreview
from aiogram_dialog.widgets.text import Const


class SG(StatesGroup):
    MAIN = State()
    SECOND = State()


window = Window(
    Const("https://nplus1.ru/news/2024/05/23/voyager-1-science-data"),
    LinkPreview(is_disabled=True),
    state=SG.MAIN,
)

second_window = Window(
    Const("some text"),
    LinkPreview(
        url=Const("https://nplus1.ru/news/2024/05/23/voyager-1-science-data"),
        prefer_small_media=True,
        show_above_text=True,
    ),
    state=SG.MAIN,
)
