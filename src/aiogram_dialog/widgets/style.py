from abc import abstractmethod

from aiogram_dialog.api.internal.widgets import StyleWidget
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.utils import add_exception_note
from aiogram_dialog.widgets.common import (
    BaseWidget,
    Whenable,
    WhenCondition,
)


class Style(Whenable, BaseWidget, StyleWidget):
    def __init__(self, when: WhenCondition = None):
        super().__init__(when=when)

    @add_exception_note
    async def render_style(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str | None:
        """
        Create button style.

        When inheriting override `_render_style` method instead
        if you want to keep processing of `when` condition
        """
        if not self.is_(data, manager):
            return None
        return await self._render_style(data, manager)

    @abstractmethod
    async def _render_style(self, data, manager: DialogManager) -> str | None:
        """
        Create button style.

        Called if widget is not hidden only (regarding `when`-condition)
        """
        raise NotImplementedError

    @add_exception_note
    async def render_emoji(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str | None:
        """
        Add custom emoji shown before the text of the button.

        When inheriting override `_render_emoji` method instead
        if you want to keep processing of `when` condition
        """
        if not self.is_(data, manager):
            return None
        return await self._render_emoji(data, manager)

    @abstractmethod
    async def _render_emoji(self, data, manager: DialogManager) -> str | None:
        """
        Add custom emoji shown before the text of the button.

        Called if widget is not hidden only (regarding `when`-condition)
        """
        raise NotImplementedError


class SimpleStyle(Style):
    def __init__(
        self,
        style: str | None = None,
        emoji_id: str | None = None,
        when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.style = style
        self.emoji_id = emoji_id

    async def _render_style(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str | None:
        return self.style

    async def _render_emoji(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str | None:
        return self.emoji_id
