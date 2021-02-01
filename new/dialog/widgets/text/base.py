from typing import Callable, Union

from dialog.widgets.when import Whenable


class Text(Whenable):
    def __init__(self, when: Union[str, Callable, None] = None):
        super().__init__(when)

    async def render_text(self, data) -> str:
        if not self.is_(data):
            return ""
        return await self._render_text(data)

    async def _render_text(self, data) -> str:
        raise NotImplementedError


class Const(Text):
    def __init__(self, text: str, when: Union[str, Callable, None] = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data) -> str:
        return self.text
