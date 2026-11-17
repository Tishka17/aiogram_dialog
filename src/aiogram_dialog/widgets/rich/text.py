from typing import Any

from aiogram.types import RichText, InputRichBlockParagraph

from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal.render import RichWidget, RenderingContext, RenderMode, RichContent
from aiogram_dialog.widgets.common import WhenCondition, Whenable



class Const(Whenable, RichWidget):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when=when)
        self.text = text

    async def render_rich(self, data: dict[str, Any], context: RenderingContext, mode: RenderMode) -> RichContent:
        if not self.is_(data, context):
            return ""

        return await self._render_rich(data, context, mode)
    async def _render_rich(self, data: dict[str, Any], context: RenderingContext, mode: RenderMode) -> RichContent:
        return RichContent(
            plain=self.text,
            blocks=[InputRichBlockParagraph(text=self.text)],  # FIXME
        )


    def supported_events(self) -> list[object]:
        return []

    async def handle_event(self, event: object, dialog_manager: DialogManager) -> None:
        pass