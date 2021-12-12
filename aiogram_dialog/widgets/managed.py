from ..manager.protocols import (
    ManagedDialogProto, DialogManager, ManagedWidgetProto,
)


class ManagedWidget(ManagedWidgetProto):
    def managed(self, dialog: ManagedDialogProto, manager: DialogManager):
        return ManagedWidgetAdapter(self, dialog, manager)


class ManagedWidgetAdapter(ManagedWidgetProto):
    def __init__(self, widget: ManagedWidget,
                 dialog: ManagedDialogProto, manager: DialogManager):
        self.widget = widget
        self.dialog = dialog
        self.manager = manager

    def __getattr__(self, item):
        return getattr(self.widget, item)
