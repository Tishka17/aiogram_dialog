import re
from typing import Optional

from .managed import ManagedWidget
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
