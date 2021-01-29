from typing import Dict, Callable, Optional

from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery

from dialog.widgets.kbd import Keyboard
from dialog.widgets.text import Text
from .dialog import Dialog, Window as WindowProtocol, DataGetter
from .manager.manager import DialogManager


class Window(WindowProtocol):

    def __init__(self, text: Optional[Text], kbd: Optional[Keyboard], state: State,
                 getter: DataGetter = None,
                 on_message: Optional[Callable] = None):
        self.text = text
        self.kbd = kbd
        self.getter = getter
        self.state = state
        self.on_message = on_message

    async def render_text(self, data) -> str:
        return await self.text.render_text(data)

    async def render_kbd(self, data) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=await self.kbd.render_kbd(data)
        )

    async def load_data(self, dialog: "Dialog", manager: DialogManager) -> Dict:
        if not self.getter:
            return {}
        return await self.getter(dialog, manager.data)

    async def process_message(self, m: Message, dialog: Dialog, manager: DialogManager):
        if self.on_message:
            await self.on_message(m, dialog, manager)

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.kbd:
            await self.kbd.process_callback(c, dialog, manager)

    async def show(self, dialog: Dialog, manager: DialogManager) -> Message:
        current_data = await self.load_data(dialog, manager)
        text = await self.render_text(current_data)
        kbd = await self.render_kbd(current_data)
        event = manager.event
        if isinstance(event, CallbackQuery):
            if text == event.message.text:
                return await event.message.edit_reply_markup(reply_markup=kbd)
            else:
                return await event.message.edit_text(text=text, reply_markup=kbd)
        else:
            context = manager.context
            if context.last_message_id:
                await manager.event.bot.edit_message_reply_markup(message_id=context.last_message_id,
                                                                  chat_id=manager.event.chat.id)
            return await manager.event.answer(text=text, reply_markup=kbd)

    def get_state(self) -> State:
        return self.state
