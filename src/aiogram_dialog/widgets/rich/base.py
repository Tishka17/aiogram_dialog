from aiogram_dialog.api.entities import RichFormat, RichParams
from aiogram_dialog.api.internal import RichWidget
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.utils import add_exception_note
from aiogram_dialog.widgets.common import BaseWidget, Whenable, WhenCondition


class BaseRich(Whenable, BaseWidget, RichWidget):
    format: RichFormat

    def __init__(
            self,
            is_rtl: bool = False,
            skip_entity_detection: bool = False,
            when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.is_rtl = is_rtl
        self.skip_entity_detection = skip_entity_detection

    @add_exception_note
    async def render_rich_params(
            self, data: dict, manager: DialogManager,
    ) -> RichParams | None:
        if not self.is_(data, manager):
            return None
        return RichParams(
            format=self.format,
            is_rtl=self.is_rtl,
            skip_entity_detection=self.skip_entity_detection,
        )


class RichHtml(BaseRich):
    format = RichFormat.HTML


class RichMarkdown(BaseRich):
    format = RichFormat.MARKDOWN


class RichBlocks(BaseRich):
    format = RichFormat.BLOCKS
