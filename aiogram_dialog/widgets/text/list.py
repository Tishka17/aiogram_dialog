from operator import itemgetter
from typing import Dict, Union, Sequence, Callable

from .base import Text
from ..when import WhenCondition

from aiogram_dialog.manager.manager import DialogManager


ItemsGetter = Callable[[Dict], Sequence]


def get_identity(items: Sequence) -> ItemsGetter:
    def identity(data) -> Sequence:
        return items
    return identity


class List(Text):
    def __init__(self, field: Text, items: Union[str, Sequence], sep: str = "\n", when: WhenCondition = None):
        super().__init__(when)
        self.field = field
        self.sep = sep
        if isinstance(items, str):
            self.items_getter = itemgetter(items)
        else:
            self.items_getter = get_identity(items)

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        texts = [
            await self.field.render_text({"data": data, "item": item, "pos": pos + 1, "pos0": pos}, manager)
            for pos, item in enumerate(self.items_getter(data))
        ]
        return self.sep.join(filter(None, texts))
