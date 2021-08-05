from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode

from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Jinja


class DialogSG(StatesGroup):
    ANIMALS = State()


# let's assume this is our window data getter
async def get_data(**kwargs):
    return {
        "title": "Animals list",
        "animals": ["cat", "dog", "my brother's tortoise"]
    }


html_text = Jinja("""
<b>{{title}}</b>
{% for animal in animals %}
* <a href="https://yandex.ru/search/?text={{ animal }}">{{ animal|capitalize }}</a>
{% endfor %}
""")

window = Window(
    html_text,
    parse_mode=ParseMode.HTML,  # do not forget to set parse mode
    state=DialogSG.ANIMALS,
    getter=get_data
)
