import re
from typing import Optional, Any

from .managed import ManagedWidget
from ..manager.protocols import DialogManager
from ..exceptions import InvalidWidgetIdError

ID_PATTERN = re.compile("^[a-zA-Z0-9_.]+$")


class Actionable(ManagedWidget):
    def __init__(self, id: Optional[str] = None):
        if id and not ID_PATTERN.match(id):
            raise InvalidWidgetIdError(f"Invalid widget id: {id}")
        self.widget_id = id

    def find(self, widget_id):
        if self.widget_id is not None and self.widget_id == widget_id:
            return self
        return None

    def get_widget_data(
            self, manager: DialogManager, default: Any,
    ) -> Any:
        """
        Returns data for current widget id, setting default if needed
        """
        return manager.current_context().widget_data.setdefault(
            self.widget_id, default,
        )

    def set_widget_data(
            self, manager: DialogManager, value: Any,
    ) -> Any:
        """
        Set data for current widget id
        """
        manager.current_context().widget_data[self.widget_id] = value

