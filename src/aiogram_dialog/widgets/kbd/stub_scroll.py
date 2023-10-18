from typing import Callable, Dict, Union

from magic_filter import MagicFilter

from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager
from .base import Keyboard
from ..common.scroll import BaseScroll, OnPageChangedVariants

PagesGetter = Callable[[Dict, "StubScroll", DialogManager], int]


def new_pages_field(fieldname: str) -> PagesGetter:
    def pages_field(
            data: Dict, widget: "StubScroll", manager: DialogManager,
    ) -> int:
        return data.get(fieldname)

    return pages_field


def new_pages_magic(f: MagicFilter) -> PagesGetter:
    def pages_magic(
            data: Dict, widget: "StubScroll", manager: DialogManager,
    ) -> int:
        return f.resolve(data)

    return pages_magic


def new_pages_fixed(pages: int) -> PagesGetter:
    def pages_fixed(
            data: Dict, widget: "StubScroll", manager: DialogManager,
    ) -> int:
        return pages

    return pages_fixed


class StubScroll(Keyboard, BaseScroll):
    def __init__(
            self,
            id: str,
            pages: Union[str, int, PagesGetter, MagicFilter],
            on_page_changed: OnPageChangedVariants = None,
    ):
        Keyboard.__init__(self, id=id, when=None)
        BaseScroll.__init__(self, id=id, on_page_changed=on_page_changed)
        if isinstance(pages, str):
            self._pages = new_pages_field(pages)
        elif isinstance(pages, MagicFilter):
            self._pages = new_pages_magic(pages)
        else:
            self._pages = new_pages_fixed(pages)

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        return [[]]

    async def get_page_count(self, data: Dict, manager: DialogManager) -> int:
        return self._pages(data, self, manager)
