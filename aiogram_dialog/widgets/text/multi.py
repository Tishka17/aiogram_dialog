from typing import Any, Callable, Dict, Hashable, Union

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from .base import Text

Selector = Callable[[Dict, "Case", DialogManager], Hashable]


def new_case_field(fieldname: str) -> Selector:
    def case_field(
            data: Dict, widget: "Case", manager: DialogManager,
    ) -> Hashable:
        return data.get(fieldname)

    return case_field


class Case(Text):
    def __init__(
            self,
            texts: Dict[Any, Text],
            selector: Union[str, Selector],
            when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.texts = texts
        if isinstance(selector, str):
            self.selector = new_case_field(selector)
        else:
            self.selector = selector

    async def _render_text(self, data, manager: DialogManager) -> str:
        selection = self.selector(data, self, manager)
        return await self.texts[selection].render_text(data, manager)
