from abc import abstractmethod
from typing import List, Optional, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.internal import KeyboardWidget
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import (
    Actionable, Whenable, WhenCondition,
)


class Keyboard(Actionable, Whenable, KeyboardWidget):
    def __init__(self, id: Optional[str] = None, when: WhenCondition = None):
        Actionable.__init__(self, id=id)
        Whenable.__init__(self, when=when)

    async def render_keyboard(
            self,
            data,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        """
        Create inline keyboard contents.

        When inheriting override `_render_keyboard` method instead
        if you want to keep processing of `when` condition
        """
        if not self.is_(data, manager):
            return []
        return await self._render_keyboard(data, manager)

    @abstractmethod
    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        """
        Create inline keyboard contents.

        Called if widget is not hidden only (regarding `when`-condition)
        """
        raise NotImplementedError

    def callback_prefix(self):
        if not self.widget_id:
            return None
        return f"{self.widget_id}:"

    def _own_callback_data(self) -> Union[str, None]:
        """Create callback data for only button in widget."""
        return self.widget_id

    def _item_callback_data(self, data: Union[str, int]):
        """Create callback data for widgets button if multiple."""
        return f"{self.callback_prefix()}{data}"

    async def process_callback(
            self,
            callback: CallbackQuery,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        if callback.data == self.widget_id:
            return await self._process_own_callback(
                callback,
                dialog,
                manager,
            )
        prefix = self.callback_prefix()
        if prefix and callback.data.startswith(prefix):
            return await self._process_item_callback(
                callback,
                callback.data[len(prefix):],
                dialog,
                manager,
            )
        return await self._process_other_callback(callback, dialog, manager)

    async def _process_own_callback(
            self,
            callback: CallbackQuery,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        """Process callback related to _own_callback_data."""
        return False

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        """Process callback related to _item_callback_data."""
        return False

    async def _process_other_callback(
            self,
            callback: CallbackQuery,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        """
        Process callback for unknown callback data.

        Can be used for layouts
        """
        return False
