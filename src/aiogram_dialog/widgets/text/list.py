from typing import Dict

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from .base import Text
from ..common.items import get_items_getter, ItemsGetterVariant


class List(Text):
    def __init__(
            self,
            field: Text,
            items: ItemsGetterVariant,
            sep: str = "\n",
            when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.field = field
        self.sep = sep
        self.items_getter = get_items_getter(items)

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
