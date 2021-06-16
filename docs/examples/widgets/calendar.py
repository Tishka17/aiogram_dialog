from datetime import date

from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar


async def on_date_selected(c: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    await c.answer(str(selected_date))

calendar = Calendar(id='calendar', on_click=on_date_selected)
