from typing import List, Optional, Union

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.manager.manager import DialogManager, ManagedDialogProto
from aiogram_dialog.widgets.action import Actionable
from aiogram_dialog.widgets.when import WhenCondition, Whenable


class Keyboard(Actionable, Whenable):
    def __init__(self, id: Optional[str] = None, when: WhenCondition = None):
        Actionable.__init__(self, id)
        Whenable.__init__(self, when)

    async def render_keyboard(
            self, data, manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        """
        Render keyboard if needed.

        When inheriting override `_render_keyboard` method instead
        if you want to keep processing of `when` condition
        """
        if not self.is_(data, manager):
            return []
        return await self._render_keyboard(data, manager)

    async def _render_keyboard(
            self, data, manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        raise NotImplementedError

    def callback_prefix(self):
        if not self.widget_id:
            return None
        return f"{self.widget_id}:"

    def _own_callback_data(self):
        """Callback data for only button in widget"""
        return self.widget_id

    def _item_callback_data(self, data: Union[str, int]):
        """Callback data for widgets button if multiple"""
        return f"{self.callback_prefix()}{data}"

    async def process_callback(
            self, c: CallbackQuery,
            dialog: ManagedDialogProto, manager: DialogManager,
    ) -> bool:
        if c.data == self.widget_id:
            return await self._process_own_callback(
                c, dialog, manager,
            )
        prefix = self.callback_prefix()
        if prefix and c.data.startswith(prefix):
            return await self._process_item_callback(
                c, c.data[len(prefix):], dialog, manager,
            )
        return await self._process_other_callback(c, dialog, manager)

    async def _process_own_callback(
            self, c: CallbackQuery, dialog: ManagedDialogProto,
            manager: DialogManager,
    ) -> bool:
        """Process callback related to _own_callback_data"""
        return False

    async def _process_item_callback(
            self, c: CallbackQuery, data: str, dialog: ManagedDialogProto,
            manager: DialogManager,
    ) -> bool:
        """Process callback related to _item_callback_data"""
        return False

    async def _process_other_callback(
            self, c: CallbackQuery, dialog: ManagedDialogProto,
            manager: DialogManager,
    ) -> bool:
        """
        Process callback for unknown callback data.

        Can be used for layouts
        """
        return False
