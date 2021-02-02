from typing import Callable, Union, Dict, Any, Hashable

from .base import Text
from ..when import WhenCondition
from ...manager.manager import DialogManager


class Multi(Text):
    def __init__(self, *texts: Text, sep="\n", when: WhenCondition = None):
        super().__init__(when)
        self.texts = texts
        self.sep = sep

    async def _render_text(self, data, manager: DialogManager) -> str:
        texts = [
            await t.render_text(data, manager)
            for t in self.texts
        ]
        return self.sep.join(filter(None, texts))


Selector = Callable[[Dict, "Case", DialogManager], Hashable]


def new_case_field(fieldname: str) -> Selector:
    def case_field(data: Dict, widget: "Case", manager: DialogManager) -> Hashable:
        return data.get(fieldname)

    return case_field


class Case(Text):
    def __init__(self, texts: Dict[Any, Text], selector: Union[str, Selector], when: WhenCondition = None):
        super().__init__(when)
        self.texts = texts
        if isinstance(selector, str):
            self.selector = new_case_field(selector)
        else:
            self.selector = selector

    async def _render_text(self, data, manager: DialogManager) -> str:
        selection = self.selector(data, self, manager)
        return await self.texts[selection].render_text(data, manager)
