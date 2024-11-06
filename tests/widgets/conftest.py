from unittest.mock import MagicMock, Mock

import pytest
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context


@pytest.fixture
def mock_manager() -> DialogManager:
    manager = MagicMock()
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
