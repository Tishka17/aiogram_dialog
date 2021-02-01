from typing import Callable, Union, Dict, Any

from .base import Text
from ..when import WhenCondition
from ...manager.manager import DialogManager


class Multi(Text):
    def __init__(self, *texts: Text, sep="\n", when: WhenCondition = None):
        super().__init__(when)
        self.texts = texts
        self.sep = sep

    async def _render_text(self, data, manager: DialogManager) -> str:
        texts = [
            await t.render_text(data, manager)
            for t in self.texts
        ]
        return self.sep.join(filter(None, texts))
