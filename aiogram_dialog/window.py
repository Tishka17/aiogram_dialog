from logging import getLogger
from typing import Dict, Callable, Optional

from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ParseMode
from aiogram.utils.exceptions import MessageNotModified

from .dialog import Dialog, DialogWindowProto, DataGetter
from .manager.intent import DialogUpdateEvent
from .widgets.action import Actionable
from .widgets.kbd import Keyboard, Row
from .widgets.text import Text, Const
from aiogram_dialog.manager.protocols import DialogManager

logger = getLogger(__name__)


class Window(DialogWindowProto):
    def __init__(self, text: Optional[Text], kbd: Optional[Keyboard], state: State,
                 getter: DataGetter = None,
                 on_message: Optional[Callable] = None,
                 parse_mode: ParseMode = None):
        if text is None:
            text = Const("")
        self.text = text
        if kbd is None:
            kbd = Row()
        self.kbd = kbd
        self.getter = getter
        self.state = state
        self.on_message = on_message
        self.parse_mode = parse_mode

    async def render_text(self, data: Dict, manager: DialogManager) -> str:
        return await self.text.render_text(data, manager)

    async def render_kbd(self, data: Dict, manager: DialogManager) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=await self.kbd.render_kbd(data, manager)
        )

    async def load_data(self, dialog: "Dialog", manager: DialogManager) -> Dict:
        if not self.getter:
            return {}
        return await self.getter(**manager.data)

    async def process_message(self, m: Message, dialog: Dialog, manager: DialogManager):
        if self.on_message:
            await self.on_message(m, dialog, manager)

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.kbd:
            await self.kbd.process_callback(c, dialog, manager)

    async def show(self, dialog: Dialog, manager: DialogManager) -> Message:
        logger.debug("Show window: %s", self)
        current_data = await self.load_data(dialog, manager)
        text = await self.render_text(current_data, manager)
        kbd = await self.render_kbd(current_data, manager)
        event = manager.event
        if isinstance(event, CallbackQuery):
            if text == event.message.text:
                if kbd != event.message.reply_markup:
                    return await event.message.edit_reply_markup(reply_markup=kbd)
                else:
                    return event.message
            else:
                return await event.message.edit_text(text=text, reply_markup=kbd, parse_mode=self.parse_mode)
        elif isinstance(event, DialogUpdateEvent) and event.message:  # cannot really check if something changed
            try:
                return await event.message.edit_text(text=text, reply_markup=kbd, parse_mode=self.parse_mode)
            except MessageNotModified:
                pass  # nothing to update
        else:
            context = manager.context
            if context and context.last_message_id:
                try:
                    await manager.event.bot.edit_message_reply_markup(message_id=context.last_message_id,
                                                                      chat_id=manager.event.chat.id)
                except MessageNotModified:
                    pass  # nothing to remove
            return await manager.event.bot.send_message(chat_id=event.chat.id, text=text, reply_markup=kbd,
                                                        parse_mode=self.parse_mode)

    def get_state(self) -> State:
        return self.state

    def find(self, widget_id) -> Optional[Actionable]:
        if self.kbd:
            return self.kbd.find(widget_id)
        return None

    def __repr__(self):
        return f"<{self.__class__.__qualname__}({self.state})>"
