from unittest.mock import AsyncMock

import pytest

from aiogram_dialog.widgets.kbd import Counter


@pytest.mark.asyncio
async def test_set_value_counter(mock_manager) -> None:
    counter = Counter(id="counter")

    assert counter.get_value(mock_manager) == 0

    await counter.set_value(mock_manager, 1)

    assert counter.get_value(mock_manager) == 1


@pytest.mark.asyncio
async def test_min_value_counter(mock_manager) -> None:
    counter = Counter(id="counter", min_value=10)

    assert counter.get_value(mock_manager) == 0

    await counter.set_value(mock_manager, 1)

    assert counter.get_value(mock_manager) == 0


@pytest.mark.asyncio
async def test_max_value_counter(mock_manager) -> None:
    counter = Counter(id="counter", max_value=10)

    assert counter.get_value(mock_manager) == 0

    await counter.set_value(mock_manager, 11)

    assert counter.get_value(mock_manager) == 0


def test_default_counter(mock_manager) -> None:
    counter = Counter(id="counter", default=10)

    assert counter.get_value(mock_manager) == 10


@pytest.mark.asyncio
async def test_on_value_changed_counter(mock_manager) -> None:
    on_value_changed = AsyncMock()
    counter = Counter(id="counter", on_value_changed=on_value_changed)

    await counter.set_value(mock_manager, 1)

    on_value_changed.assert_called_once()
