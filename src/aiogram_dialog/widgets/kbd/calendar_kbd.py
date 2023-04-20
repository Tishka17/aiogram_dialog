from calendar import monthcalendar
from datetime import date
from time import mktime
from typing import Awaitable, Callable, Dict, List, TypedDict, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor,
    WidgetEventProcessor,
)
from .base import Keyboard

OnDateSelected = Callable[
    [ChatEvent, "ManagedCalendarAdapter", DialogManager,
     date], Awaitable,
]

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


class Calendar(Keyboard):
    def __init__(
            self,
            id: str,
            min_date: date = date.min,
            max_date: date = date.max,
            on_click: Union[OnDateSelected, WidgetEventProcessor, None] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self.min_date = min_date
        self.max_date = max_date
        self.on_click = ensure_event_processor(on_click)

    async def _render_keyboard(
            self, data: Dict, manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        offset = self.get_offset(manager)
        current_scope = self.get_scope(manager)

        if current_scope == SCOPE_DAYS:
            return self.days_kbd(offset)
        elif current_scope == SCOPE_MONTHS:
            return self.months_kbd(offset)
        elif current_scope == SCOPE_YEARS:
            return self.years_kbd(offset)

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        current_offset = self.get_offset(manager)

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
                new_offset = date(
                    current_offset.year, (current_offset.month - 1), 1,
                )
                self.set_offset(new_offset, manager)

        elif data in [SCOPE_MONTHS, SCOPE_YEARS]:
            self.set_scope(data, manager)

        elif data.startswith(PREFIX_MONTH):
            data = int(data[len(PREFIX_MONTH):])
            new_offset = date(current_offset.year, data, 1)
            self.set_scope(SCOPE_DAYS, manager)
            self.set_offset(new_offset, manager)

        elif data.startswith(PREFIX_YEAR):
            data = int(data[len(PREFIX_YEAR):])
            new_offset = date(data, 1, 1)
            self.set_scope(SCOPE_MONTHS, manager)
            self.set_offset(new_offset, manager)

        else:
            raw_date = int(data)
            await self.on_click.process_event(
                callback,
                self.managed(manager),
                manager,
                date.fromtimestamp(raw_date),
            )
        return True

    def years_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        years = []
        for n in range(offset.year - 7, offset.year + 7, 3):
            year_row = []
            for year in range(n, n + 3):
                if self.min_date.year <= year <= self.max_date.year:
                    year_row.append(
                        InlineKeyboardButton(
                            text=str(year),
                            callback_data=self._item_callback_data(
                                f"{PREFIX_YEAR}{year}",
                            ),
                        ),
                    )
                else:
                    year_row.append(
                        InlineKeyboardButton(
                            text=" ",
                            callback_data=" ",
                        ),
                    )

            years.append(year_row)
        return years

    def months_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        header_year = offset.strftime("year %Y")
        months = []
        for n in MONTHS_NUMBERS:
            season = []
            for month in n:
                if self.min_date.month <= month <= self.max_date.month:
                    month_text = date(offset.year, month, 1).strftime("%B")
                    season.append(
                        InlineKeyboardButton(
                            text=month_text,
                            callback_data=self._item_callback_data(
                                f"{PREFIX_MONTH}{month}",
                            ),
                        ),
                    )
                else:
                    season.append(
                        InlineKeyboardButton(
                            text=" ",
                            callback_data=" ",
                        ),
                    )

            months.append(season)
        return [
            [
                InlineKeyboardButton(
                    text=header_year,
                    callback_data=self._item_callback_data(SCOPE_YEARS),
                ),
            ],
            *months,
        ]

    def days_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        header_week = offset.strftime("%B %Y")
        weekheader = [
            InlineKeyboardButton(text=dayname, callback_data=" ")
            for dayname in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ]
        days = []
        for week in monthcalendar(offset.year, offset.month):
            week_row = []
            for day in week:
                if day == 0 or not self.min_date <= date(offset.year, offset.month, day) <= self.max_date:
                    week_row.append(
                        InlineKeyboardButton(
                            text=" ",
                            callback_data=" ",
                        ),
                    )
                else:
                    raw_date = int(
                        mktime(
                            date(offset.year, offset.month, day).timetuple(),
                        ),
                    )
                    week_row.append(
                        InlineKeyboardButton(
                            text=str(day),
                            callback_data=self._item_callback_data(raw_date),
                        ),
                    )
            days.append(week_row)
        return [
            [
                InlineKeyboardButton(
                    text=header_week,
                    callback_data=self._item_callback_data(SCOPE_MONTHS),
                ),
            ],
            weekheader,
            *days,
            [
                InlineKeyboardButton(
                    text="Prev month",
                    callback_data=self._item_callback_data(MONTH_PREV),
                ),
                InlineKeyboardButton(
                    text="Zoom out",
                    callback_data=self._item_callback_data(SCOPE_MONTHS),
                ),
                InlineKeyboardButton(
                    text="Next month",
                    callback_data=self._item_callback_data(MONTH_NEXT),
                ),
            ],
        ]

    def get_scope(self, manager: DialogManager) -> str:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        current_scope = calendar_data.get("current_scope")
        return current_scope or SCOPE_DAYS

    def get_offset(self, manager: DialogManager) -> date:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        current_offset = calendar_data.get("current_offset")
        if current_offset is None:
            if (date.today() < self.max_date):
                return date.today()
            else:
                return self.max_date
        return date.fromisoformat(current_offset)

    def set_offset(self, new_offset: date,
                   manager: DialogManager) -> None:
        data = self.get_widget_data(manager, {})
        if date(self.min_date.year, self.min_date.month, 1) <= new_offset <= date(self.max_date.year, self.max_date.month, 1):
            data["current_offset"] = new_offset.isoformat()

    def set_scope(self, new_scope: str, manager: DialogManager) -> None:
        data = self.get_widget_data(manager, {})
        data["current_scope"] = new_scope

    def managed(self, manager: DialogManager):
        return ManagedCalendarAdapter(self, manager)


class ManagedCalendarAdapter(ManagedWidget[Calendar]):
    def get_scope(self) -> str:
        return self.widget.get_scope(self.manager)

    def get_offset(self) -> date:
        return self.widget.get_offset(self.manager)

    def set_offset(
            self, new_offset: date,
    ) -> None:
        return self.widget.set_offset(new_offset, self.manager)

    def set_scope(
            self, new_scope: str,
    ) -> None:
        return self.widget.set_scope(new_scope, self.manager)
