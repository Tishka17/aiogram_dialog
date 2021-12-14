from typing import TypeVar, Generic

from ..manager.protocols import (
    ManagedDialogProto, DialogManager, ManagedWidgetProto,
)


class ManagedWidget(ManagedWidgetProto):
    def managed(self, manager: DialogManager):
        return ManagedWidgetAdapter(self, manager)


W = TypeVar("W", bound=ManagedWidget)


class ManagedWidgetAdapter(ManagedWidgetProto, Generic[W]):
    def __init__(self, widget: W, manager: DialogManager):
        self.widget = widget
        self.manager = manager

    def __getattr__(self, item):
        return getattr(self.widget, item)
