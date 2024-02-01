import pytest

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Jinja


@pytest.fixture()
def mock_manager(mock_manager) -> DialogManager:
    mock_manager.middleware_data = {}
    return mock_manager


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
