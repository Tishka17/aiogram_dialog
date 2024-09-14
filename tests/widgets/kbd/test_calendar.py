import pytest

from aiogram_dialog.widgets.kbd import Calendar, CalendarScope


@pytest.mark.asyncio
async def test_render_calendar(mock_manager):
    calendar = Calendar(id="calendar")
    res_days = await calendar.render_keyboard(data={}, manager=mock_manager)
    assert res_days
    calendar.set_scope(CalendarScope.MONTHS, mock_manager)
    res_months = await calendar.render_keyboard(data={}, manager=mock_manager)
    assert res_months
    assert res_months != res_days
    calendar.set_scope(CalendarScope.YEARS, mock_manager)
    res_years = await calendar.render_keyboard(data={}, manager=mock_manager)
    assert res_years
    assert res_years != res_days
    assert res_years != res_months
