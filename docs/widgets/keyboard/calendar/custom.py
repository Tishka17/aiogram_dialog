from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import (
    Calendar,
    CalendarScope,
    CalendarUserConfig,
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
)
from aiogram_dialog.widgets.text import Const, Format


class CustomCalendar(Calendar):
    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data, self.config,
                today_text=Format("***"),
                header_text=Format("> {date: %B %Y} <"),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data, self.config,
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data, self.config,
            ),
        }

    async def _get_user_config(
            self,
            data: dict,
            manager: DialogManager,
    ) -> CalendarUserConfig:
        return CalendarUserConfig(
            firstweekday=7,
        )
