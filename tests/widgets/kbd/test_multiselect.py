import operator
from unittest.mock import AsyncMock

import pytest
from aiogram.types import TelegramObject

from aiogram_dialog.widgets.kbd import Multiselect
from aiogram_dialog.widgets.text import Format


@pytest.mark.asyncio
async def test_check_multiselect(mock_manager) -> None:
    multiselect = Multiselect(
        Format("✓ {item[1]}"),
        Format("{item[1]}"),
        id="fruit",
        item_id_getter=operator.itemgetter(0),
        items=[("1", "Apple"), ("2", "Banana"), ("3", "Orange")],
    )

    assert multiselect.get_checked(mock_manager) == []

    await multiselect.set_checked(TelegramObject(), "1", True, mock_manager)
    await multiselect.set_checked(TelegramObject(), "3", True, mock_manager)

    assert multiselect.get_checked(mock_manager) == ["1", "3"]


@pytest.mark.asyncio
async def test_min_selected_multiselect(mock_manager) -> None:
    multiselect = Multiselect(
        Format("✓ {item[1]}"),
        Format("{item[1]}"),
        id="fruit",
        item_id_getter=operator.itemgetter(0),
        items=[("1", "Apple"), ("2", "Banana"), ("3", "Orange")],
        min_selected=2,
    )

    await multiselect.set_checked(TelegramObject(), "1", True, mock_manager)
    await multiselect.set_checked(TelegramObject(), "3", True, mock_manager)

    assert multiselect.get_checked(mock_manager) == ["1", "3"]

    await multiselect.set_checked(TelegramObject(), "3", False, mock_manager)

    assert multiselect.get_checked(mock_manager) == ["1", "3"]


@pytest.mark.asyncio
async def test_max_selected_multiselect(mock_manager) -> None:
    multiselect = Multiselect(
        Format("✓ {item[1]}"),
        Format("{item[1]}"),
        id="fruit",
        item_id_getter=operator.itemgetter(0),
        items=[("1", "Apple"), ("2", "Banana"), ("3", "Orange")],
        max_selected=2,
    )

    await multiselect.set_checked(TelegramObject(), "1", True, mock_manager)
    await multiselect.set_checked(TelegramObject(), "3", True, mock_manager)

    assert multiselect.get_checked(mock_manager) == ["1", "3"]

    await multiselect.set_checked(TelegramObject(), "2", True, mock_manager)

    assert multiselect.get_checked(mock_manager) == ["1", "3"]


@pytest.mark.asyncio
async def test_reset_checked_multiselect(mock_manager) -> None:
    multiselect = Multiselect(
        Format("✓ {item[1]}"),
        Format("{item[1]}"),
        id="fruit",
        item_id_getter=operator.itemgetter(0),
        items=[("1", "Apple"), ("2", "Banana"), ("3", "Orange")],
    )

    await multiselect.set_checked(TelegramObject(), "1", True, mock_manager)
    await multiselect.set_checked(TelegramObject(), "3", True, mock_manager)

    assert multiselect.get_checked(mock_manager) == ["1", "3"]

    await multiselect.reset_checked(TelegramObject(), mock_manager)

    assert multiselect.get_checked(mock_manager) == []


@pytest.mark.asyncio
async def test_on_state_changed_multiselect(mock_manager) -> None:
    on_state_changed = AsyncMock()
    multiselect = Multiselect(
        Format("✓ {item[1]}"),
        Format("{item[1]}"),
        id="fruit",
        item_id_getter=operator.itemgetter(0),
        items=[("1", "Apple"), ("2", "Banana"), ("3", "Orange")],
        on_state_changed=on_state_changed,
    )

    await multiselect.set_checked(TelegramObject(), "1", True, mock_manager)

    on_state_changed.assert_called_once()


@pytest.mark.asyncio
async def test_render_multiselect(mock_manager) -> None:
    multiselect = Multiselect(
        Format("✓ {item[1]}"),
        Format("{item[1]}"),
        id="fruit",
        item_id_getter=operator.itemgetter(0),
        items=[("1", "Apple"), ("2", "Banana"), ("3", "Orange")],
    )

    keyboard = await multiselect.render_keyboard(data={}, manager=mock_manager)

    await multiselect.set_checked(TelegramObject(), "1", True, mock_manager)
    await multiselect.set_checked(TelegramObject(), "3", True, mock_manager)

    assert keyboard[0][0].text == "✓ Apple"
    assert keyboard[0][1].text == "Banana"
    assert keyboard[0][2].text == "✓ Orange"
