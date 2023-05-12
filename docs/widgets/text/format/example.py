from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Format


async def getter_example(**kwargs):
    return {
        "name": "Tishka17",
    }


window = Window(
    Format("Hello, {name}!"),
    getter=getter_example,
    ...
)
