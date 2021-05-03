from datetime import date, datetime
from time import mktime
from calendar import monthcalendar
from typing import List, Callable, Union, Awaitable

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.manager.intent import ChatEvent
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor, ensure_event_processor
from .base import Keyboard

OnDateSelected = Callable[[ChatEvent, "MonthCalendar", DialogManager, date], Awaitable]

LEVEL = "LEVEL"
YEARS_LEVEL = "Y"
MONTHS_LEVEL = "M"
YEAR_PREFIX = "YEAR:"
MONTH_PREFIX = "MONTH:"
NEXT_MONTH = "+"
PREV_MONTH = "-"
OFFSET = "OFFSET"
MONTHS_LIST = [range(i, i + 3) for i in range(1, 13, 3)]

class MonthCalendar(Keyboard):
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
        if manager.context.data(f"{self.widget_id}:{LEVEL}", None, internal=True) == YEARS_LEVEL:
            rendered_kbd = self.years_kbd(offset)
        elif manager.context.data(f"{self.widget_id}:{LEVEL}", None, internal=True) == MONTHS_LEVEL:
            rendered_kbd = self.months_kbd(offset) 
        else:
            rendered_kbd = self.days_kbd(offset)
        return rendered_kbd

    async def process_callback(self, 
                               c: CallbackQuery, 
                               dialog: Dialog,
                               manager: DialogManager) -> bool:
        prefix = f"{self.widget_id}:"
        offset = self.get_offset(manager)
        if not c.data.startswith(prefix):
            return False
        data = c.data[len(prefix):]
        if data == NEXT_MONTH:
            self.set_offset(datetime(offset.year + (offset.month // 12), ((offset.month % 12) + 1), 1), manager)
        elif data == PREV_MONTH:
            if offset.month == 1:
                self.set_offset(datetime(offset.year - 1, 12, 1), manager)
            else:
                self.set_offset(datetime(offset.year, (offset.month - 1), 1), manager)
        elif data == MONTHS_LEVEL:
            manager.context.set_data(f"{self.widget_id}:{LEVEL}", data, internal=True)
        elif data == YEARS_LEVEL:
            manager.context.set_data(f"{self.widget_id}:{LEVEL}", data, internal=True)
        elif data.startswith(MONTH_PREFIX):
            data = int(c.data[len(prefix) + len(MONTH_PREFIX):])
            self.set_month(offset, data, manager)
        elif data.startswith(YEAR_PREFIX):
            data = int(c.data[len(prefix) + len(YEAR_PREFIX):])
            self.set_year(offset, data, manager)
        else:
            raw_date = int(data)
            manager.context.set_data(self.widget_id, date.fromtimestamp(raw_date), internal=True)
            await self.on_click.process_event(c, self, manager, date.fromtimestamp(raw_date))

    def years_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        years = []
        for n in range(offset.year - 7, offset.year + 7, 3):
            year_row = []
            for y in range(n, n+3):
                year_text = date(y, 1, 1).strftime("%Y")
                year_row.append(InlineKeyboardButton(text=f"{year_text}",
                                                     callback_data=f"{self.widget_id}:{YEAR_PREFIX}{y}"))
            years.append(year_row)
        return years

    def months_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        header_year = offset.strftime("year %Y")
        months = []
        for n in MONTHS_LIST:
            season = []
            for m in n:
                month_text = date(offset.year, m, 1).strftime("%B")
                season.append(InlineKeyboardButton(text=f"{month_text}",
                                                   callback_data=f"{self.widget_id}:{MONTH_PREFIX}{m}"))
            months.append(season)
        return [[InlineKeyboardButton(text=header_year, callback_data=f"{self.widget_id}:{YEARS_LEVEL}"),],
                *months]

    def days_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        header_week = offset.strftime("%B %Y")
        weekheader = [InlineKeyboardButton(text=dayname, callback_data=" ")
                      for dayname in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]]
        days = []
        for w in monthcalendar(offset.year, offset.month):
            week_row = []
            for d in w:
                if d == 0:
                    week_row.append(InlineKeyboardButton(text=" ",
                                                         callback_data=" "))
                else:
                    raw_date = int(mktime(date(offset.year, offset.month, d).timetuple()))
                    week_row.append(InlineKeyboardButton(text=str(d),
                                                         callback_data=f"{self.widget_id}:{raw_date}"))
            days.append(week_row)
        return [
            [
                InlineKeyboardButton(text=header_week,
                                     callback_data=f"{self.widget_id}:{MONTHS_LEVEL}"),
            ],
            weekheader,
            *days,
            [
                InlineKeyboardButton(text="Prev month",
                                     callback_data=f"{self.widget_id}:{PREV_MONTH}"),
                InlineKeyboardButton(text="Zoom out",
                                     callback_data=f"{self.widget_id}:{MONTHS_LEVEL}"),
                InlineKeyboardButton(text="Next month",
                                     callback_data=f"{self.widget_id}:{NEXT_MONTH}"),
            ],
        ]

    def get_offset(self, 
                   manager: DialogManager) -> date:
        raw_date = manager.context.data(f"{self.widget_id}:{OFFSET}", None, internal=True)
        if raw_date is None:
            return date.today()
        return date.fromtimestamp(raw_date)

    def set_offset(self, 
                   offset: date, 
                   manager: DialogManager) -> None:
        raw_date = int(mktime(offset.timetuple()))
        manager.context.set_data(f"{self.widget_id}:{OFFSET}", raw_date, internal=True)
    
    def set_month(self,
                  offset: date,
                  data: int,
                  manager: DialogManager) -> None:
        manager.context.set_data(f"{self.widget_id}:{LEVEL}", False, internal=True)
        self.set_offset(datetime(offset.year, data, 1), manager)
    
    def set_year(self,
                 offset: date,
                 data: int,
                 manager: DialogManager) -> None:
        manager.context.set_data(f"{self.widget_id}:{LEVEL}", MONTHS_LEVEL, internal=True)
        self.set_offset(datetime(data, 1, 1), manager)

    def get_date(self, 
                 manager: DialogManager) -> Optional[date]:
        return manager.context.data(self.widget_id, None, internal=True)
