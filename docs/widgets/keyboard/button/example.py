from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const


async def go_clicked(callback: CallbackQuery, button: Button,
                     manager: DialogManager):
    await callback.message.answer("Going on!")


go_btn = Button(
    Const("Go"),
    id="go",  # id is used to detect which button is clicked
    on_click=go_clicked,
)
