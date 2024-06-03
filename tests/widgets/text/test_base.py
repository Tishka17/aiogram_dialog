import pytest
from aiogram import F

from aiogram_dialog.widgets.text import Const


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
