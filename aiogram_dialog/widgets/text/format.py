from typing import Dict

from .base import Text
from ..when import WhenCondition
from ...manager.manager import DialogManager


class Format(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        return self.text.format_map(data)
