from aiogram.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery

from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Button, Back
from aiogram_dialog.widgets.text import Const, Format

class MySG(StatesGroup):
    window1 = State()
    window2 = State()


async def window1_get_data(**kwargs):
    return {
        "something": "data from Window1 getter",
    }


async def window2_get_data(**kwargs):
    return {
        "something": "data from Window2 getter",
    }


async def dialog_get_data(**kwargs):
    return {
        "name": "Tishka17",
    }


async def button1_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Add data to `dialog_data` and switch to the next window of current dialog """
    manager.dialog_data['user_input'] = 'some data from user, stored in `dialog_data`'
    await manager.next()


dialog = Dialog(
    Window(
        Format("Hello, {name}!"),
        Format("Something: {something}"),        
        Button(Const("Next window"), id="button1", on_click=button1_clicked),
        state=MySG.window1,
        getter=window1_get_data,  # here we specify data getter for window1
    ),
    Window(
        Format("Hello, {name}!"),
        Format("Something: {something}"),        
        Format("User input: {dialog_data[user_input]}"),
        Back(text=Const("Back")),
        state=MySG.window2,
        getter=window2_get_data,  # here we specify data getter for window2
    ),
    getter=dialog_get_data  # here we specify data getter for dialog
)