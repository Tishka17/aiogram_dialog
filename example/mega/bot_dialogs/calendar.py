from datetime import date
from typing import Dict

from aiogram.types import CallbackQuery
from babel.dates import get_day_names, get_month_names

from aiogram_dialog import (
    Dialog, Window, DialogManager,
)
from aiogram_dialog.widgets.kbd import (
    Calendar, CalendarScope, ManagedCalendar, SwitchTo,
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView, CalendarMonthView, CalendarScopeView, CalendarYearsView,
)
from aiogram_dialog.widgets.text import Const, Text, Format
from . import states
from .common import MAIN_MENU_BUTTON


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_day_names(
            width="short", context='stand-alone', locale=locale,
        )[selected_date.weekday()].title()


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_month_names(
            'wide', context='stand-alone', locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data, self.config,
                header_text="~~~~~ " + Month() + " ~~~~~",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data, self.config,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data, self.config,
            ),
        }


async def on_date_selected(
        callback: CallbackQuery, widget: ManagedCalendar,
        manager: DialogManager,
        selected_date: date,
):
    await callback.answer(str(selected_date))


CALENDAR_MAIN_MENU_BUTTON = SwitchTo(
    text=Const("Back"), id="back", state=states.Calendar.MAIN,
)
calendar_dialog = Dialog(
    Window(
        Const("Select calendar configuration"),
        SwitchTo(
            Const("Default"),
            id="default",
            state=states.Calendar.DEFAULT
        ),
        SwitchTo(
            Const("Customized"),
            id="custom",
            state=states.Calendar.CUSTOM
        ),
        MAIN_MENU_BUTTON,
        state=states.Calendar.MAIN,
    ),
    Window(
        Const("Default calendar widget"),
        Calendar(
            id="cal",
            on_click=on_date_selected,
        ),
        CALENDAR_MAIN_MENU_BUTTON,
        state=states.Calendar.DEFAULT,
    ),
    Window(
        Const("Customized calendar widget"),
        Const("Here we use custom text widgets to localize "),
        CustomCalendar(
            id="cal",
            on_click=on_date_selected,
        ),
        CALENDAR_MAIN_MENU_BUTTON,
        state=states.Calendar.CUSTOM,
    ),
)
