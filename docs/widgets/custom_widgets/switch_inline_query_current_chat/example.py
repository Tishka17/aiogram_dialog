from aiogram.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import SwitchInlineQuery
from aiogram_dialog.widgets.text import Const


class SwitchInlineQueryCurrentChat(SwitchInlineQuery):
    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> list[list[InlineKeyboardButton]]:
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
            Const("query"),  # additional query. Optional
        ),
        state=MySG.main,
    ),
)
