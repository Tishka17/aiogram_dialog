from typing import Dict, List

from aiogram.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram_dialog import Dialog, Window
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import SwitchInlineQuery
from aiogram_dialog.widgets.text import Const


class SwitchInlineQueryCurrentChat(SwitchInlineQuery):
    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    switch_inline_query_current_chat=await self.switch_inline.render_text(
                        data, manager,
                    ),
                ),
            ],
        ]


class MySG(StatesGroup):
    main = State()


dialog = Dialog(
    Window(
        SwitchInlineQueryCurrentChat(
            Const("Some search"),  # Button text
            Const("query")  # additinal query. Optional
        ),
        state=MySG.main
    )
)
