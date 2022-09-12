from typing import Any, Generic, TypeVar

from aiogram_dialog.api.protocols import ActiveDialogManager


class ManagedWidget:
    def managed(self, manager: ActiveDialogManager) -> Any:
        return ManagedWidgetAdapter(self, manager)


W = TypeVar("W", bound=ManagedWidget)


class ManagedWidgetAdapter(Generic[W]):
    def __init__(self, widget: W, manager: ActiveDialogManager):
        self.widget = widget
        self.manager = manager

    def __getattr__(self, item):
        return getattr(self.widget, item)
