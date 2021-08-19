from abc import ABC
from calendar import monthcalendar
from datetime import date
from time import mktime
from typing import List, Callable, Union, Awaitable, TypedDict

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.context.events import ChatEvent
from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor, ensure_event_processor
from .base import Keyboard

OnDateSelected = Callable[[ChatEvent, "MonthCalendar", DialogManager, date], Awaitable]

# Constants for managing widget rendering scope
SCOPE_DAYS = "SCOPE_DAYS"
SCOPE_MONTHS = "SCOPE_MONTHS"
SCOPE_YEARS = "SCOPE_YEARS"

# Constants for scrolling months
MONTH_NEXT = "+"
MONTH_PREV = "-"

# Constants for prefixing month and year values
PREFIX_MONTH = "MONTH"
PREFIX_YEAR = "YEAR"

MONTHS_NUMBERS = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)]


class CalendarData(TypedDict):
    current_scope: str
    current_offset: str


class Calendar(Keyboard, ABC):
    def __init__(self,
                 id: str,
                 on_click: Union[OnDateSelected, WidgetEventProcessor, None] = None,
                 when: Union[str, Callable] = None):
        super().__init__(id, when)
        self.on_click = ensure_event_processor(on_click)

    async def render_keyboard(self,
                              data,
                              manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        offset = self.get_offset(manager)
        current_scope = self.get_scope(manager)

        if current_scope == SCOPE_DAYS:
            return self.days_kbd(offset)
        elif current_scope == SCOPE_MONTHS:
            return self.months_kbd(offset)
        elif current_scope == SCOPE_YEARS:
            return self.years_kbd(offset)

    async def process_callback(self,
                               c: CallbackQuery,
                               dialog: Dialog,
                               manager: DialogManager) -> bool:
        prefix = f"{self.widget_id}:"
        if not c.data.startswith(prefix):
            return False
        current_offset = self.get_offset(manager)
        data = c.data[len(prefix):]

        if data == MONTH_NEXT:
            new_offset = date(
                year=current_offset.year + (current_offset.month // 12),
                month=((current_offset.month % 12) + 1),
                day=1,
            )
            self.set_offset(new_offset, manager)

        elif data == MONTH_PREV:
            if current_offset.month == 1:
                new_offset = date(current_offset.year - 1, 12, 1)
                self.set_offset(new_offset, manager)
            else:
                new_offset = date(current_offset.year, (current_offset.month - 1), 1)
                self.set_offset(new_offset, manager)

        elif data in [SCOPE_MONTHS, SCOPE_YEARS]:
            self.set_scope(data, manager)

        elif data.startswith(PREFIX_MONTH):
            data = int(c.data[len(prefix) + len(PREFIX_MONTH):])
            new_offset = date(current_offset.year, data, 1)
            self.set_scope(SCOPE_DAYS, manager)
            self.set_offset(new_offset, manager)

        elif data.startswith(PREFIX_YEAR):
            data = int(c.data[len(prefix) + len(PREFIX_YEAR):])
            new_offset = date(data, 1, 1)
            self.set_scope(SCOPE_MONTHS, manager)
            self.set_offset(new_offset, manager)

        else:
            raw_date = int(data)
            await self.on_click.process_event(c, self, manager, date.fromtimestamp(raw_date))
        return True

    def years_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        years = []
        for n in range(offset.year - 7, offset.year + 7, 3):
            year_row = []
            for year in range(n, n + 3):
                year_row.append(InlineKeyboardButton(text=str(year),
                                                     callback_data=f"{self.widget_id}:{PREFIX_YEAR}{year}"))
            years.append(year_row)
        return years

    def months_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        header_year = offset.strftime("year %Y")
        months = []
        for n in MONTHS_NUMBERS:
            season = []
            for month in n:
                month_text = date(offset.year, month, 1).strftime("%B")
                season.append(InlineKeyboardButton(text=month_text,
                                                   callback_data=f"{self.widget_id}:{PREFIX_MONTH}{month}"))
            months.append(season)
        return [
            [
                InlineKeyboardButton(text=header_year,
                                     callback_data=f"{self.widget_id}:{SCOPE_YEARS}"),
            ],
            *months
        ]

    def days_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        header_week = offset.strftime("%B %Y")
        weekheader = [InlineKeyboardButton(text=dayname, callback_data=" ")
                      for dayname in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]]
        days = []
        for week in monthcalendar(offset.year, offset.month):
            week_row = []
            for day in week:
                if day == 0:
                    week_row.append(InlineKeyboardButton(text=" ",
                                                         callback_data=" "))
                else:
                    raw_date = int(mktime(date(offset.year, offset.month, day).timetuple()))
                    week_row.append(InlineKeyboardButton(text=str(day),
                                                         callback_data=f"{self.widget_id}:{raw_date}"))
            days.append(week_row)
        return [
            [
                InlineKeyboardButton(text=header_week,
                                     callback_data=f"{self.widget_id}:{SCOPE_MONTHS}"),
            ],
            weekheader,
            *days,
            [
                InlineKeyboardButton(text="Prev month",
                                     callback_data=f"{self.widget_id}:{MONTH_PREV}"),
                InlineKeyboardButton(text="Zoom out",
                                     callback_data=f"{self.widget_id}:{SCOPE_MONTHS}"),
                InlineKeyboardButton(text="Next month",
                                     callback_data=f"{self.widget_id}:{MONTH_NEXT}"),
            ],
        ]

    def get_scope(self, manager: DialogManager) -> str:
        calendar_data: CalendarData = manager.current_context().widget_data.get(self.widget_id, {})
        current_scope = calendar_data.get("current_scope")
        return current_scope or SCOPE_DAYS

    def get_offset(self, manager: DialogManager) -> date:
        calendar_data: CalendarData = manager.current_context().widget_data.get(self.widget_id, {})
        current_offset = calendar_data.get("current_offset")
        if current_offset is None:
            return date.today()
        return date.fromisoformat(current_offset)

    def set_offset(self, new_offset: date, manager: DialogManager) -> None:
        data = manager.current_context().widget_data.setdefault(self.widget_id, {})
        data["current_offset"] = new_offset.isoformat()

    def set_scope(self, new_scope: str, manager: DialogManager) -> None:
        data = manager.current_context().widget_data.setdefault(self.widget_id, {})
        data["current_scope"] = new_scope
