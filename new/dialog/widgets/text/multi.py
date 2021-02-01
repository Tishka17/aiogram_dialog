from typing import Callable, Union

from .base import Text


class Multi(Text):
    def __init__(self, *texts: Text, sep="\n", when: Union[str, Callable, None] = None):
        super().__init__(when)
        self.texts = texts
        self.sep = sep

    async def _render_text(self, data) -> str:
        texts = [
            await t.render_text(data)
            for t in self.texts
        ]
        return self.sep.join(filter(None, texts))
