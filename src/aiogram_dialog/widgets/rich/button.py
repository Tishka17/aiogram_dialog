from typing import Any

from aiogram.types import RichText, InputRichBlockParagraph, RichMessageButton, RichTextButton

from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal.render import RichWidget, RenderingContext, RenderMode, RichContent
from aiogram_dialog.widgets.common import WhenCondition, Whenable



class Button(Whenable, RichWidget):
    def __init__(self, text: RichWidget, when: WhenCondition = None):
        super().__init__(when=when)
        self.text = text

    async def render_rich(self, data: dict[str, Any], context: RenderingContext, mode: RenderMode) -> RichContent:
        if not self.is_(data, context):
            return ""

        return await self._render_rich(data, context, mode)
    async def _render_rich(self, data: dict[str, Any], context: RenderingContext, mode: RenderMode) -> RichContent:
        text = await self.text.render_rich(data, context, mode)
        if mode is RenderMode.RICH_BLOCKS:
            return RichContent(
                plain=self.text,
                blocks=[InputRichBlockParagraph(text=RichTextButton(
                    button=RichMessageButton(
                        text=text.blocks,
                        callback_data="1",
                    )
                ))],  # FIXME
                media=text.media,
            )
        elif mode is RenderMode.RICH_HTML or mode is RenderMode.RICH_MD:
            return RichContent(
                plain=f"""<tg-button type="callback_data" data="1">{text.plain}</tg-button>""",
                media=text.media,
            )
        else:
            raise ValueError("Unknown mode")


    def supported_events(self) -> list[object]:
        return []

    async def handle_event(self, event: object, dialog_manager: DialogManager) -> None:
        pass