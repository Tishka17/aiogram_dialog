from unittest.mock import MagicMock, Mock

import pytest
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.text import Jinja


@pytest.fixture()
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
    manager.middleware_data = {}

    return manager


@pytest.mark.asyncio
async def test_render_jinja(mock_manager) -> None:
    jinja = Jinja("""
<b>{{title}}</b>
{% for animal in animals %}
* <a href="https://yandex.ru/search/?text={{ animal }}">{{ animal|capitalize }}</a>
{% endfor %}
""")  # noqa: E501

    data = {
        "title": "Animals list",
        "animals": ["cat", "dog", "my brother's tortoise"],
    }

    rendered_text = await jinja.render_text(
        data=data, manager=mock_manager,
    )

    assert rendered_text == """
<b>Animals list</b>
* <a href="https://yandex.ru/search/?text=cat">Cat</a>
* <a href="https://yandex.ru/search/?text=dog">Dog</a>
* <a href="https://yandex.ru/search/?text=my brother&#39;s tortoise">My brother&#39;s tortoise</a>
"""  # noqa: E501
