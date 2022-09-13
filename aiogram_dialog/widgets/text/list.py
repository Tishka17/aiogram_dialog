from operator import itemgetter
from typing import Callable, Dict, Sequence, Union

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from .base import Text

ItemsGetter = Callable[[Dict], Sequence]


def get_identity(items: Sequence) -> ItemsGetter:
    def identity(data) -> Sequence:
        return items

    return identity


class List(Text):
    def __init__(
            self,
            field: Text,
            items: Union[str, Callable, Sequence],
            sep: str = "\n",
            when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.field = field
        self.sep = sep
        if isinstance(items, str):
            self.items_getter = itemgetter(items)
        elif isinstance(items, Callable):
            self.items_getter = items
        else:
            self.items_getter = get_identity(items)

    async def _render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        texts = [
            await self.field.render_text(
                {"data": data, "item": item, "pos": pos + 1, "pos0": pos},
                manager,
            )
            for pos, item in enumerate(self.items_getter(data))
        ]
        return self.sep.join(filter(None, texts))
