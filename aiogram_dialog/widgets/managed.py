from typing import Any, Generic, TypeVar

from aiogram_dialog.api.protocols import DialogManager


class ManagedWidget:
    def managed(self, manager: DialogManager) -> Any:
        return ManagedWidgetAdapter(self, manager)


W = TypeVar("W", bound=ManagedWidget)


class ManagedWidgetAdapter(Generic[W]):
    def __init__(self, widget: W, manager: DialogManager):
        self.widget = widget
        self.manager = manager

    def __getattr__(self, item):
        return getattr(self.widget, item)
