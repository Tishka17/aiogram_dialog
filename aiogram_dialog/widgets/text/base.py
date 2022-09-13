from typing import Dict, Union

from aiogram_dialog.api.internal import TextWidget
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import (
    BaseWidget, true_condition, Whenable, WhenCondition,
)


class Text(Whenable, BaseWidget, TextWidget):
    def __init__(self, when: WhenCondition = None):
        super().__init__(when=when)

    async def render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        """
        Create text.

        When inheriting override `_render_text` method instead
        if you want to keep processing of `when` condition
        """
        if not self.is_(data, manager):
            return ""
        return await self._render_text(data, manager)

    async def _render_text(self, data, manager: DialogManager) -> str:
        """
        Create text.

        Called if widget is not hidden only (regarding `when`-condition)
        """
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
        super().__init__(when=when)
        self.text = text

    async def _render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        return self.text


class Multi(Text):
    def __init__(self, *texts: Text, sep="\n", when: WhenCondition = None):
        super().__init__(when=when)
        self.texts = texts
        self.sep = sep

    async def _render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        texts = [await t.render_text(data, manager) for t in self.texts]
        return self.sep.join(filter(None, texts))

    def __iadd__(self, other: Union["Text", str]):
        if isinstance(other, str):
            other = Const(other)
        self.texts += (other,)

    def __add__(self, other: Union["Text", str]):
        if isinstance(other, str):
            other = Const(other)
        if self.condition is true_condition and self.sep == "":
            # reduce nesting
            return Multi(*self.texts, other, sep="")
        else:
            return Multi(self, other, sep="")

    def __radd__(self, other: Union["Text", str]):
        if isinstance(other, str):
            other = Const(other)
        if self.condition is true_condition and self.sep == "":
            # reduce nesting
            return Multi(other, *self.texts, sep="")
        else:
            return Multi(other, self, sep="")
