from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import List, Format


async def getter_example(**kwargs):
    return {
        "user_info": (
            ("name", "Tishka17"),
            ("username", "@Tishka17"),
        )
    }


dialog = Dialog(
    Window(
        List(
            Format("+ {item[0]} - {item[1]}"),
            items="user_info",
        ),
        getter=getter_example,
        ...
    ),
)
