from typing import Any

from aiogram.filters.state import StatesGroup, State

from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.text import Format

class MySG(StatesGroup):
    main = State()


async def getter_example(**kwargs):
    return {
        "name": "Tishka17",
    }


window = Window(
    Format("Hello, {name}!"),
    Format('Project: {dialog_data[project][name]}'),
    getter=getter_example,
    state=MySG.main
)


async def on_dialog_start(start_data: Any, manager: DialogManager):
    project = {
        'name': 'aiogram-dialog',
    }
    manager.dialog_data['project'] = project


dialog = Dialog(
    window,
    on_start=on_dialog_start
)
