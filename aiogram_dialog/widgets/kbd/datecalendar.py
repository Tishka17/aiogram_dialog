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

class MonthCalendar(Keyboard):
    def __init__(self,
                 id: str,
                 on_click: Union[OnDateSelected, WidgetEventProcessor, None] = None,
                 when: Union[str, Callable] = None):
        super().__init__(id, when)
        self.on_click = ensure_event_processor(on_click)

    async def render_keyboard(self, data,
                              manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        offset = self.get_offset(manager)
        if manager.context.data("outscope", None, internal=True) == "Y":
            years = []
            for n in [[*range(i, i + 3)] for i in range(offset.year - 7, offset.year + 7, 3)]:
                year_row = []
                for y in n:
                    year_text = date(y, 1, 1).strftime("%Y")
                    year_row.append(InlineKeyboardButton(text=f"{year_text}",
                                                         callback_data=f"{self.widget_id}:year:{y}"))
                years.append(year_row)

            res = [
                *years,
            ]

        elif manager.context.data("outscope", None, internal=True) == "M":
            header_year = offset.strftime("year %Y")
            months = []
            for n in [[*range(i, i + 3)] for i in range(1, 13, 3)]:
                season = []
                for m in n:
                    month_text = date(offset.year, m, 1).strftime("%B")
                    season.append(InlineKeyboardButton(text=f"{month_text}",
                                                       callback_data=f"{self.widget_id}:month:{m}"))
                months.append(season)

            res = [
                [
                    InlineKeyboardButton(text=header_year, callback_data=f"{self.widget_id}:zoom_years"),
                ],
                *months,
            ]

        else:
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
                        raw_data = int(mktime(date(offset.year, offset.month, d).timetuple()))
                        week_row.append(InlineKeyboardButton(text=str(d),
                                                             callback_data=f"{self.widget_id}:{raw_data}"))
                days.append(week_row)

            res = [
                [
                    InlineKeyboardButton(text=header_week,
                                         callback_data=f"{self.widget_id}:zoom_one_year"),
                ],
                weekheader,
                *days,
                [
                    InlineKeyboardButton(text="Prev month",
                                         callback_data=f"{self.widget_id}:-"),
                    InlineKeyboardButton(text="Zoom out",
                                         callback_data=f"{self.widget_id}:zoom_one_year"),
                    InlineKeyboardButton(text="Next month",
                                         callback_data=f"{self.widget_id}:+"),
                ],
            ]

        return res

    async def process_callback(self, c: CallbackQuery, dialog: Dialog,
                               manager: DialogManager) -> bool:
        prefix = f"{self.widget_id}:"
        offset = self.get_offset(manager)
        if not c.data.startswith(prefix):
            return False
        data = c.data[len(prefix):]
        if data == "+":
            self.set_offset(datetime(offset.year + (offset.month // 12), ((offset.month % 12) + 1), 1), manager)
        elif data == "-":
            if offset.month == 1:
                self.set_offset(datetime(offset.year - 1, 12, 1), manager)
            else:
                self.set_offset(datetime(offset.year, (offset.month - 1), 1), manager)
        elif data == "zoom_one_year":
            manager.context.set_data("outscope", "M", internal=True)
        elif data == "zoom_years":
            manager.context.set_data("outscope", "Y", internal=True)
        elif "month" in data:
            data = int(c.data[len(prefix) + 6:])
            manager.context.set_data("outscope", False, internal=True)
            self.set_offset(datetime(offset.year, data, 1), manager)
        elif "year" in data:
            data = int(c.data[len(prefix) + 5:])
            manager.context.set_data("outscope", "M", internal=True)
            self.set_offset(datetime(data, 1, 1), manager)
        else:
            raw_date = int(data)
            manager.context.set_data(f"{self.widget_id}-selected", raw_date)
            await self.on_click.process_event(c, self, manager, date.fromtimestamp(raw_date))

    def get_offset(self, manager: DialogManager) -> date:
        raw_date = manager.context.data(self.widget_id, None, internal=True)
        if raw_date is None:
            return date.today()
        return date.fromtimestamp(raw_date)

    def set_offset(self, offset: date, manager: DialogManager):
        raw_date = int(mktime(offset.timetuple()))
        manager.context.set_data(self.widget_id, raw_date, internal=True)
