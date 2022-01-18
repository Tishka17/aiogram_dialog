from typing import Optional, Any

from aiogram.dispatcher.filters.state import State

from aiogram_dialog.deprecation_utils import manager_deprecated
from aiogram_dialog.manager.protocols import (
    ManagedDialogProto, DialogManager, ManagedDialogAdapterProto,
)


class ManagedDialogAdapter(ManagedDialogAdapterProto):
    def __init__(self, dialog: ManagedDialogProto, manager: DialogManager):
        self.dialog = dialog
        self.manager = manager

    async def show(self, preview: bool = False,
                   manager: Optional[DialogManager] = None):
        manager_deprecated(manager)
        return await self.dialog.show(self.manager)

    async def next(self,
                   manager: Optional[DialogManager] = None):
        manager_deprecated(manager)
        return await self.dialog.next(self.manager)

    async def back(self,
                   manager: Optional[DialogManager] = None):
        manager_deprecated(manager)
        return await self.dialog.back(self.manager)

    async def switch_to(self, state: State,
                        manager: Optional[DialogManager] = None):
        manager_deprecated(manager)
        return await self.dialog.switch_to(state, self.manager)

    def find(self, widget_id,
             manager: Optional[DialogManager] = None) -> Optional[Any]:
        manager_deprecated(manager)
        widget = self.dialog.find(widget_id)
        if widget is None:
            return None
        return widget.managed(self.manager)
