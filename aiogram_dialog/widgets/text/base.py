from typing import Union, Dict

from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.when import Whenable, WhenCondition, true


class Text(Whenable):
    def __init__(self, when: WhenCondition = None):
        super().__init__(when)

    async def render_text(self, data: Dict, manager: DialogManager) -> str:
        if not self.is_(data, manager):
            return ""
        return await self._render_text(data, manager)

    async def _render_text(self, data, manager: DialogManager) -> str:
        raise NotImplementedError

    def __add__(self, other: Union["Text", str]):
        if isinstance(other, str):
            other = Const(other)
        return Multi(self, other, sep="")

    def __radd__(self, other: Union["Text", str]):
        if isinstance(other, str):
            other = Const(other)
        return Multi(other, self, sep="")


class Const(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        return self.text


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

    def __iadd__(self, other: Union["Text", str]):
        if isinstance(other, str):
            other = Const(other)
        self.texts += (other,)

    def __add__(self, other: Union["Text", str]):
        if isinstance(other, str):
            other = Const(other)
        if self.condition is true and self.sep == "":
            # reduce nesting
            return Multi(*self.texts, other, sep="")
        else:
            return Multi(self, other, sep="")

    def __radd__(self, other: Union["Text", str]):
        if isinstance(other, str):
            other = Const(other)
        if self.condition is true and self.sep == "":
            # reduce nesting
            return Multi(other, *self.texts, sep="")
        else:
            return Multi(other, self, sep="")
