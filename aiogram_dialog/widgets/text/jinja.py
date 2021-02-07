from typing import Dict

from .base import Text
from ..when import WhenCondition
from ...manager.manager import DialogManager
from jinja2 import Template


class Jinja(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        # TODO Environment
        # from file
        # custom filters
        super().__init__(when)
        self.template = Template(text, trim_blocks=True, lstrip_blocks=True,autoescape=True)

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        return self.template.render(data)
