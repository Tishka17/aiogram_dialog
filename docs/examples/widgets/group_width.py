from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const

group = Group(
    Button(Const("Crawl"), id="crawl"),
    Button(Const("Go"), id="go"),
    Button(Const("Run"), id="run"),
    Button(Const("Fly"), id="fly"),
    Button(Const("Teleport"), id="tele"),
    keep_rows=False,
    width=2,
)
