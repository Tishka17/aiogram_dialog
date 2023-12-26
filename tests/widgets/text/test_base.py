from unittest.mock import Mock

import pytest
from aiogram import F
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
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
async def test_add_const(mock_manager):
    text = Const("Hello, ") + Const("world!")
    res = await text.render_text({}, mock_manager)
    assert res == "Hello, world!"


@pytest.mark.asyncio
async def test_add_add(mock_manager):
    text = Const("Hello, ") + Const("world") + Const("!")
    res = await text.render_text({}, mock_manager)
    assert res == "Hello, world!"


@pytest.mark.asyncio
async def test_add_str(mock_manager):
    text = Const("Hello, ") + "world!"
    res = await text.render_text({}, mock_manager)
    assert res == "Hello, world!"


@pytest.mark.asyncio
async def test_add_str_rght(mock_manager):
    text = "Hello, " + Const("world!")
    res = await text.render_text({}, mock_manager)
    assert res == "Hello, world!"


@pytest.mark.asyncio
async def test_or(mock_manager):
    text = Const("A") | Const("B")
    res = await text.render_text({}, mock_manager)
    assert res == "A"


@pytest.mark.asyncio
async def test_ror_str(mock_manager):
    text = "A" | Const("B")
    res = await text.render_text({}, mock_manager)
    assert res == "A"


@pytest.mark.asyncio
async def test_or_condition(mock_manager):
    text = (
        Const("A", when=F["a"]) |
        Const("B", when=F["b"]) |
        Const("C")
    )
    res = await text.render_text({"a": True}, mock_manager)
    assert res == "A"
    res = await text.render_text({"b": True}, mock_manager)
    assert res == "B"
    res = await text.render_text({}, mock_manager)
    assert res == "C"
