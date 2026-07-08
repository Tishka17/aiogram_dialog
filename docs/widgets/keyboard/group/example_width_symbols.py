from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const

# Rows are wrapped by total text length instead of a fixed button count.
# "Crawl"(5) + "Go"(2) + "Run"(3) = 10 -> first row; "Teleport"(8) -> next row.
group = Group(
    Button(Const("Crawl"), id="crawl"),
    Button(Const("Go"), id="go"),
    Button(Const("Run"), id="run"),
    Button(Const("Teleport"), id="tele"),
    width_symbols=10,
)
