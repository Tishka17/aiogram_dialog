import re
from typing import Optional

from .when import Whenable, WhenCondition

ID_PATTERN = re.compile("^[a-zA-Z0-9_.]+$")


class Actionable(Whenable):
    def __init__(self, id: Optional[str] = None, when: WhenCondition = None):
        super().__init__(when)
        if id and not ID_PATTERN.match(id):
            raise ValueError(f"Invalid widget id: {id}")
        self.widget_id = id

    def find(self, widget_id):
        if self.widget_id is not None and self.widget_id == widget_id:
            return self
        return None
