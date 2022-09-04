from typing import Dict, Any

from .base import Text, Values
from ..when import WhenCondition
from ...manager.manager import DialogManager

I18N_FORMAT_KEY = "aiogd_i18n_format"


def default_format_text(text: str, data: Values) -> str:
    return text.format_map(data)


class _FormatDataStub:
    def __init__(self, name="", data=None):
        self.name = name
        self.data = data or {}

    def __getitem__(self, item: Any) -> Any:
        if item in self.data:
            return self.data[item]
        if not self.name:
            return _FormatDataStub(item)
        return _FormatDataStub(f"{self.name}[{item}]")

    def __getattr__(self, item):
        return _FormatDataStub(f"{self.name}.{item}")

    def __format__(self, format_spec):
        if format_spec:
            res = f"{self.name}:{format_spec}"
        else:
            res = self.name
        return f"{{{res}}}"


class Format(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        format_text = manager.data.get(I18N_FORMAT_KEY, default_format_text)
        if manager.is_preview():
            return format_text(self.text, _FormatDataStub(data=data))

        return format_text(self.text, data)
