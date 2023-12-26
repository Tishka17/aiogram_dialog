from unittest.mock import Mock

import pytest
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.kbd import Calendar, CalendarScope


@pytest.fixture()
def mock_manager() -> DialogManager:
    manager = Mock()
    context = Context(
        dialog_data={},
        start_data={},
        widget_data={},
        state=State(),
        _stack_id="_stack_id",
        _intent_id="_intent_id",
    )
    manager.current_context = Mock(side_effect=lambda: context)

    return manager


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
