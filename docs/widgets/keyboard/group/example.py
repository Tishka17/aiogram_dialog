from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const

group = Group(
    Row(
        Button(Const("Go"), id="go"),
        Button(Const("Run"), id="run"),
    ),
    Button(Const("Fly"), id="fly"),
)