import locale
from calendar import MONDAY
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from time import mktime
from typing import Optional, Tuple, Dict, List, Protocol, TypedDict

from aiogram.types import InlineKeyboardButton, CallbackQuery

EMPTY_BUTTON = InlineKeyboardButton(text=" ", callback_data="", )

from aiogram_dialog import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import ManagedWidget
from aiogram_dialog.widgets.kbd import Keyboard
from aiogram_dialog.widgets.text import Text, Format
from aiogram_dialog.widgets.widget_event import ensure_event_processor

CALLBACK_NEXT_MONTH = "+"
CALLBACK_PREV_MONTH = "-"
CALLBACK_NEXT_YEAR = "+Y"
CALLBACK_PREV_YEAR = "-Y"
CALLBACK_NEXT_YEARS_PAGE = "+YY"
CALLBACK_PREV_YEARS_PAGE = "-YY"
CALLBACK_SCOPE_MONTHS = "M"
CALLBACK_SCOPE_YEARS = "Y"

CALLBACK_PREFIX_MONTH = "MONTH"
CALLBACK_PREFIX_YEAR = "YEAR"

BEARING_DATE = date(2018, 1, 1)


class Scope(Enum):
    DAYS = "DAYS"
    MONTHS = "MONTHS"
    YEARS = "YEARS"


def month_begin(offset: date):
    return offset.replace(day=1)


def next_month_begin(offset: date):
    return month_begin(month_begin(offset) + timedelta(days=31))


def prev_month_begin(offset: date):
    return month_begin(month_begin(offset) - timedelta(days=1))


class different_locale:
    def __init__(self, other_locale):
        self.locale = other_locale

    def __enter__(self):
        self.oldlocale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, self.locale)

    def __exit__(self, *args):
        locale.setlocale(locale.LC_TIME, self.oldlocale)


class CalendarData(TypedDict):
    current_scope: str
    current_offset: str


@dataclass(frozen=True)
class CalendarConfig:
    min_date = date(1900, 1, 1)
    max_date = date(2100, 12, 31)
    firstweekday: int = MONDAY
    month_columns: int = 3
    locale: Optional[str] = None
    scopes: Tuple[Scope, ...] = tuple(Scope)
    years_per_page = 20
    years_columns = 5


class ScopeView(Protocol):
    async def render(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        pass


class DaysView(ScopeView):
    def __init__(
            self,
            calendar: Keyboard,
            date_text: Text = Format("{date:%d}"),
            weekday_text: Text = Format("{date:%a}"),
            header_text: Text = Format("{date:%B %Y}"),
            zoom_out_text: Text = Format("Zoom out"),
            next_month_text: Text = Format(">>"),
            prev_month_text: Text = Format("<<"),
    ):
        self.zoom_out_text = zoom_out_text
        self.next_month_text = next_month_text
        self.prev_month_text = prev_month_text
        self.calendar = calendar
        self.date_text = date_text
        self.weekday_text = weekday_text
        self.header_text = header_text

    async def _render_date_button(
            self, selected_date: date, data: Dict, manager: DialogManager,
    ) -> InlineKeyboardButton:
        current_data = {
            "date": selected_date,
            "data": data,
        }
        raw_date = int(mktime(selected_date.timetuple()))
        return InlineKeyboardButton(
            text=await self.date_text.render_text(
                current_data, manager,
            ),
            callback_data=self.calendar._item_callback_data(str(raw_date)),
        )

    async def _render_days(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        keyboard = []
        # align beginning
        start_date = offset.replace(day=1)  # month beginning
        min_date = max(config.min_date, start_date)
        days_since_week_start = start_date.weekday() - config.firstweekday
        if days_since_week_start < 0:
            days_since_week_start += 7
        start_date -= timedelta(days=days_since_week_start)
        end_date = next_month_begin(offset) - timedelta(days=1)
        # align ending
        max_date = min(config.max_date, end_date)
        days_since_week_start = end_date.weekday() - config.firstweekday
        days_till_week_end = (7 - days_since_week_start) % 7
        end_date += timedelta(days=days_till_week_end)
        # add days
        for offset in range(0, (end_date - start_date).days, 7):
            row = []
            for row_offset in range(7):
                days_offset = timedelta(days=(offset + row_offset))
                current_date = start_date + days_offset
                if min_date <= current_date <= max_date:
                    row.append(await self._render_date_button(
                        current_date, data, manager,
                    ))
                else:
                    row.append(EMPTY_BUTTON)
            keyboard.append(row)
        return keyboard

    async def _render_week_header(
            self,
            config: CalendarConfig,
            data: Dict,
            manager: DialogManager,
    ) -> List[InlineKeyboardButton]:
        week_range = range(config.firstweekday, config.firstweekday + 7)
        header = []
        for week_day in week_range:
            week_day = week_day % 7 + 1
            data = {
                "week_day": week_day,
                "date": BEARING_DATE.replace(day=week_day),
                "data": data,
            }
            header.append(InlineKeyboardButton(
                text=await self.weekday_text.render_text(data, manager),
                callback_data="",
            ))
        return header

    async def _render_pager(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[InlineKeyboardButton]:
        curr_month = offset.month
        next_month = (curr_month % 12) + 1
        prev_month = (curr_month - 2) % 12 + 1
        prev_end = month_begin(offset) - timedelta(1)
        next_begin = next_month_begin(offset)
        if prev_end < config.min_date and next_begin > config.max_date:
            return []

        prev_month_data = {
            "mongth": prev_month,
            "date": BEARING_DATE.replace(month=prev_month),
            "data": data,
        }
        curr_month_data = {
            "month": curr_month,
            "date": BEARING_DATE.replace(month=curr_month),
            "data": data,
        }
        next_month_data = {
            "month": next_month,
            "date": BEARING_DATE.replace(month=next_month),
            "data": data,
        }
        if prev_end < config.min_date:
            prev_button = EMPTY_BUTTON
        else:
            prev_button = InlineKeyboardButton(
                text=await self.prev_month_text.render_text(
                    prev_month_data, manager,
                ),
                callback_data=self.calendar._item_callback_data(
                    CALLBACK_PREV_MONTH,
                ),
            )
        zoom_button = InlineKeyboardButton(
            text=await self.zoom_out_text.render_text(
                curr_month_data, manager,
            ),
            callback_data=self.calendar._item_callback_data(
                CALLBACK_SCOPE_MONTHS,
            ),
        )
        if next_begin > config.max_date:
            next_button = EMPTY_BUTTON
        else:
            next_button = InlineKeyboardButton(
                text=await self.next_month_text.render_text(
                    next_month_data, manager,
                ),
                callback_data=self.calendar._item_callback_data(
                    CALLBACK_PREV_MONTH,
                ),
            )

        return [prev_button, zoom_button, next_button]

    async def _render_header(
            self, config, offset, data, manager,
    ) -> List[InlineKeyboardButton]:
        data = {
            "date": offset,
            "data": data,
        }
        return [InlineKeyboardButton(
            text=await self.header_text.render_text(data, manager),
            callback_data=self.calendar._item_callback_data(
                CALLBACK_SCOPE_MONTHS,
            ),
        )]

    async def render(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [
            await self._render_header(config, offset, data, manager),
            await self._render_week_header(config, data, manager),
            *await self._render_days(config, offset, data, manager),
            await self._render_pager(config, offset, data, manager),
        ]


class MonthView(ScopeView):
    def __init__(
            self,
            calendar: Keyboard,
            month_text: Text = Format("{date:%B}"),
            header_text: Text = Format("{date:%Y}"),
            zoom_out_text: Text = Format("Zoom out"),
            next_year_text: Text = Format("{date:%Y} >>"),
            prev_year_text: Text = Format("<< {date:%Y}"),
    ):
        self.calendar = calendar
        self.month_text = month_text
        self.header_text = header_text
        self.zoom_out_text = zoom_out_text
        self.next_year_text = next_year_text
        self.prev_year_text = prev_year_text

    async def _render_pager(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[InlineKeyboardButton]:
        curr_year = offset.year
        next_year = curr_year + 1
        prev_year = curr_year - 1

        if not (config.min_date.year <= curr_year <= config.max_date.year):
            return []

        prev_year_data = {
            "year": prev_year,
            "date": BEARING_DATE.replace(year=prev_year),
            "data": data,
        }
        curr_year_data = {
            "year": curr_year,
            "date": BEARING_DATE.replace(year=curr_year),
            "data": data,
        }
        next_year_data = {
            "year": next_year,
            "date": BEARING_DATE.replace(year=next_year),
            "data": data,
        }
        if prev_year < config.min_date.year:
            prev_button = EMPTY_BUTTON
        else:
            prev_button = InlineKeyboardButton(
                text=await self.prev_year_text.render_text(
                    prev_year_data, manager,
                ),
                callback_data=self.calendar._item_callback_data(
                    CALLBACK_PREV_YEAR,
                ),
            )
        if next_year > config.max_date.year:
            next_button = EMPTY_BUTTON
        else:
            next_button = InlineKeyboardButton(
                text=await self.next_year_text.render_text(
                    next_year_data, manager,
                ),
                callback_data=self.calendar._item_callback_data(
                    CALLBACK_NEXT_YEAR,
                ),
            )
        zoom_button = InlineKeyboardButton(
            text=await self.zoom_out_text.render_text(
                curr_year_data, manager,
            ),
            callback_data=self.calendar._item_callback_data(
                CALLBACK_SCOPE_YEARS,
            ),
        )
        return [prev_button, zoom_button, next_button]

    def _is_month_allowed(
            self, config: CalendarConfig, offset: date, month: int,
    ) -> bool:
        start = date(offset.year, month, 1)
        end = next_month_begin(offset) - timedelta(days=1)
        return start >= config.min_date and end <= config.max_date

    async def _render_months(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        keyboard = []
        for row in range(1, 13, config.month_columns):
            keyboard_row = []
            for column in range(config.month_columns):
                month = row + column
                if self._is_month_allowed(config, offset, month):
                    month_data = {
                        "month": month,
                        "date": BEARING_DATE.replace(month=month),
                        "data": data,
                    }
                    keyboard_row.append(InlineKeyboardButton(
                        text=await self.month_text.render_text(
                            month_data, manager,
                        ),
                        callback_data=self.calendar._item_callback_data(
                            f"{CALLBACK_PREFIX_MONTH}{month}",
                        ),
                    ))
                else:
                    keyboard_row.append(EMPTY_BUTTON)
            keyboard.append(keyboard_row)
        return keyboard

    async def _render_header(
            self, config, offset, data, manager,
    ) -> List[InlineKeyboardButton]:
        data = {
            "date": offset,
            "data": data,
        }
        return [InlineKeyboardButton(
            text=await self.header_text.render_text(data, manager),
            callback_data=self.calendar._item_callback_data(
                CALLBACK_SCOPE_YEARS,
            ),
        )]

    async def render(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [
            await self._render_header(config, offset, data, manager),
            *await self._render_months(config, offset, data, manager),
            await self._render_pager(config, offset, data, manager),
        ]


class YearsView(ScopeView):
    def __init__(
            self,
            calendar: Keyboard,
            year_text: Text = Format("{date:%Y}"),
            next_page_text: Text = Format(">>"),
            prev_page_text: Text = Format("<<"),
    ):
        self.calendar = calendar
        self.year_text = year_text
        self.next_page_text = next_page_text
        self.prev_page_text = prev_page_text

    async def _render_pager(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[InlineKeyboardButton]:
        curr_year = offset.year
        next_year = curr_year + config.years_per_page
        prev_year = curr_year - config.years_per_page

        prev_year_data = {
            "year": prev_year,
            "date": BEARING_DATE.replace(year=prev_year),
            "data": data,
        }
        next_year_data = {
            "year": next_year,
            "date": BEARING_DATE.replace(year=next_year),
            "data": data,
        }
        if curr_year <= config.min_date.year:
            prev_button = EMPTY_BUTTON
        else:
            prev_button = InlineKeyboardButton(
                text=await self.prev_page_text.render_text(
                    prev_year_data, manager,
                ),
                callback_data=self.calendar._item_callback_data(
                    CALLBACK_PREV_YEARS_PAGE,
                ),
            )
        if next_year > config.max_date.year:
            next_button = EMPTY_BUTTON
        else:
            next_button = InlineKeyboardButton(
                text=await self.next_page_text.render_text(
                    next_year_data, manager,
                ),
                callback_data=self.calendar._item_callback_data(
                    CALLBACK_NEXT_YEARS_PAGE,
                ),
            )

        if prev_button == next_button == EMPTY_BUTTON:
            return []
        return [prev_button, next_button]

    def _is_year_allowed(
            self, config: CalendarConfig, offset: date, year: int,
    ) -> bool:
        return config.min_date.year <= year <= config.max_date.year

    async def _render_years(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        keyboard = []

        for row in range(0, config.years_per_page, config.years_columns):
            keyboard_row = []
            for column in range(config.years_columns):
                curr_year = offset.year + row + column

                month_data = {
                    "year": curr_year,
                    "date": BEARING_DATE.replace(year=curr_year),
                    "data": data,
                }
                if self._is_year_allowed(config, offset, curr_year):
                    keyboard_row.append(InlineKeyboardButton(
                        text=await self.year_text.render_text(
                            month_data, manager,
                        ),
                        callback_data=self.calendar._item_callback_data(
                            f"{CALLBACK_PREFIX_YEAR}{curr_year}",
                        )
                    ))
                else:
                    keyboard_row.append(EMPTY_BUTTON)
            keyboard.append(keyboard_row)
        return keyboard

    async def render(
            self,
            config: CalendarConfig,
            offset: date,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [
            *await self._render_years(config, offset, data, manager),
            await self._render_pager(config, offset, data, manager),
        ]


class Calendar(Keyboard):
    def __init__(
            self,
            id: str,
            on_click=None,
            config: CalendarConfig = CalendarConfig(),
            when=None,
    ):
        super().__init__(id=id, when=when)
        self.on_click = ensure_event_processor(on_click)
        self.config = config
        self.views = self._init_views()

    def _init_views(self) -> Dict[Scope, ScopeView]:
        return {
            Scope.DAYS: DaysView(self),
            Scope.MONTHS: MonthView(self),
            Scope.YEARS: YearsView(self),
        }

    async def _get_config(
            self, data: Dict, manager: DialogManager,
    ) -> CalendarConfig:
        return self.config

    async def _render_keyboard(
            self,
            data,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        scope = self.get_scope(manager)
        view = self.views[scope]
        offset = self.get_offset(manager)
        config = await self._get_config(data, manager)
        with different_locale(config.locale):
            return await view.render(
                config, offset, data, manager
            )

    def get_scope(self, manager: DialogManager) -> Scope:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        current_scope = calendar_data.get("current_scope")
        if not current_scope:
            return Scope.DAYS
        try:
            return Scope(current_scope)
        except ValueError:
            # LOG
            return Scope.DAYS

    def get_offset(self, manager: DialogManager) -> date:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        current_offset = calendar_data.get("current_offset")
        if current_offset is None:
            return date.today()
        return date.fromisoformat(current_offset)

    def set_offset(self, new_offset: date,
                   manager: DialogManager) -> None:
        data = self.get_widget_data(manager, {})
        data["current_offset"] = new_offset.isoformat()

    def set_scope(self, new_scope: Scope, manager: DialogManager) -> None:
        data = self.get_widget_data(manager, {})
        data["current_scope"] = new_scope.value

    def managed(self, manager: DialogManager):
        return ManagedCalendarAdapter(self, manager)

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        offset = self.get_offset(manager)
        config = self.config

        if data == CALLBACK_SCOPE_MONTHS:
            self.set_scope(Scope.MONTHS, manager)
        elif data == CALLBACK_SCOPE_YEARS:
            self.set_scope(Scope.YEARS, manager)
        elif data == CALLBACK_PREV_MONTH:
            offset = month_begin(month_begin(offset) - timedelta(days=1))
            self.set_offset(offset, manager)
        elif data == CALLBACK_NEXT_MONTH:
            offset = next_month_begin(offset)
            self.set_offset(offset, manager)
        elif data == CALLBACK_NEXT_YEAR:
            offset = offset.replace(offset.year + 1)
            self.set_offset(offset, manager)
        elif data == CALLBACK_PREV_YEAR:
            offset = offset.replace(offset.year - 1)
            self.set_offset(offset, manager)
        elif data == CALLBACK_NEXT_YEARS_PAGE:
            offset = offset.replace(offset.year + config.years_per_page)
            self.set_offset(offset, manager)
        elif data == CALLBACK_PREV_YEARS_PAGE:
            offset = offset.replace(offset.year - config.years_per_page)
            self.set_offset(offset, manager)
        elif data.startswith(CALLBACK_PREFIX_MONTH):
            month = int(data[len(CALLBACK_PREFIX_MONTH):])
            offset = date(offset.year, month, 1)
            self.set_offset(offset, manager)
            self.set_scope(Scope.DAYS, manager)
        elif data.startswith(CALLBACK_PREFIX_YEAR):
            year = int(data[len(CALLBACK_PREFIX_YEAR):])
            offset = date(year, 1, 1)
            self.set_offset(offset, manager)
            self.set_scope(Scope.MONTHS, manager)
        else:
            raw_date = int(data)
            await self.on_click.process_event(
                callback,
                self.managed(manager),
                manager,
                date.fromtimestamp(raw_date),
            )

        return True


class ManagedCalendarAdapter(ManagedWidget[Calendar]):
    def get_scope(self) -> Scope:
        """Get current scope showing in calendar."""
        return self.widget.get_scope(self.manager)

    def get_offset(self) -> date:
        """Get current offset from which calendar is shown."""
        return self.widget.get_offset(self.manager)

    def set_offset(
            self, new_offset: date,
    ) -> None:
        """Set current offset for calendar paging."""
        return self.widget.set_offset(new_offset, self.manager)

    def set_scope(
            self, new_scope: Scope,
    ) -> None:
        """Set current scope showing in calendar."""
        return self.widget.set_scope(new_scope, self.manager)
