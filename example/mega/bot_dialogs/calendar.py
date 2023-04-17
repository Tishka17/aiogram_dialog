from datetime import date

from aiogram.types import CallbackQuery

from aiogram_dialog import (
    Dialog, Window, DialogManager,
)
from aiogram_dialog.widgets.kbd import (
    Calendar, ManagedCalendarAdapter,
)
from aiogram_dialog.widgets.text import Const
from . import states
from .common import MAIN_MENU_BUTTON


async def on_date_selected(
        callback: CallbackQuery, widget: ManagedCalendarAdapter,
        manager: DialogManager,
        selected_date: date,
):
    await callback.answer(str(selected_date))


calendar_dialog = Dialog(
    Window(
        Const("Calendar widget"),
        Calendar(
            id="cal",
            on_click=on_date_selected,
        ),
        MAIN_MENU_BUTTON,
        state=states.Calendar.MAIN,
    ),
)
