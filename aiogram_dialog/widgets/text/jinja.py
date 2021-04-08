from typing import Dict, Any, Iterable, Optional, Callable, Union, Tuple, Mapping

from aiogram import Bot
from jinja2 import Environment, BaseLoader

from .base import Text
from ..when import WhenCondition
from ...manager.manager import DialogManager

BOT_ENV_FIELD = "DialogsJinjaEnvironment"

Filter = Callable[..., str]
Filters = Union[Iterable[Tuple[str, Filter]], Mapping[str, Filter]]


class Jinja(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        # TODO Environment
        # from file
        # custom filters
        super().__init__(when)
        self.template_text = text

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        env: Environment = manager.event.bot[BOT_ENV_FIELD]
        template = env.get_template(self.template_text)
        return template.render(data)


class StubLoader(BaseLoader):
    def get_source(self, environment, template):
        return template, template, lambda: True


def setup_jinja(
        bot: Bot,
        *args: Any,
        filters: Optional[Filters] = None,
        **kwargs: Any,
) -> Environment:
    kwargs.setdefault("autoescape", True)
    kwargs.setdefault("lstrip_blocks", True)
    kwargs.setdefault("trim_blocks", True)
    if not "loader" in kwargs:
        kwargs["loader"] = StubLoader()
    env = Environment(*args, **kwargs)
    if filters is not None:
        env.filters.update(filters)

    bot[BOT_ENV_FIELD] = env
    return env
