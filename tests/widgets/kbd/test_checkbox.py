from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.fsm.state import State
from aiogram.types import TelegramObject

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.kbd import Checkbox
from aiogram_dialog.widgets.text import Const


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
async def test_check_checkbox(mock_manager) -> None:
    checkbox = Checkbox(
        Const("✓  Checked"),
        Const("Unchecked"),
        id="check",
        default=True,
    )

    assert checkbox.is_checked(mock_manager)

    await checkbox.set_checked(TelegramObject(), False, mock_manager)

    assert not checkbox.is_checked(mock_manager)


@pytest.mark.asyncio
async def test_on_state_changed_checkbox(mock_manager) -> None:
    on_state_changed = AsyncMock()
    checkbox = Checkbox(
        Const("✓  Checked"),
        Const("Unchecked"),
        id="check",
        on_state_changed=on_state_changed,
    )

    await checkbox.set_checked(TelegramObject(), False, mock_manager)

    on_state_changed.assert_called_once()
