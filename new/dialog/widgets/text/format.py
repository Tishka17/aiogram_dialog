from typing import Callable, Union

from .base import Text


class Format(Text):
    def __init__(self, text: str, when: Union[str, Callable, None] = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data) -> str:
        return self.text.format_map(data)
