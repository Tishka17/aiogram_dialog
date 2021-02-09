from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const

column = Column(
    Button(Const("Go"), id="go"),
    Button(Const("Run"), id="run"),
    Button(Const("Fly"), id="fly"),
)
