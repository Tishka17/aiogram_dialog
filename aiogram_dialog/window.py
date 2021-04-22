from logging import getLogger
from typing import Dict, Optional, Union

from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ParseMode
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeEdited

from aiogram_dialog.manager.protocols import DialogManager
from .dialog import Dialog, DialogWindowProto, DataGetter
from .manager.intent import DialogUpdateEvent
from .widgets.action import Actionable
from .widgets.input import BaseInput, MessageHandlerFunc
from .widgets.kbd import Keyboard
from .widgets.text import Text
from .widgets.utils import ensure_widgets

logger = getLogger(__name__)


class Window(DialogWindowProto):
    def __init__(self,
                 *widgets: Union[str, Text, Keyboard, MessageHandlerFunc, BaseInput],
                 state: State,
                 getter: DataGetter = None,
                 parse_mode: ParseMode = None):
        self.text, self.keyboard, self.on_message = ensure_widgets(widgets)
        self.getter = getter
        self.state = state
        self.parse_mode = parse_mode

    async def render_text(self, data: Dict, manager: DialogManager) -> str:
        return await self.text.render_text(data, manager)

    async def render_kbd(self, data: Dict, manager: DialogManager) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=await self.keyboard.render_keyboard(data, manager)
        )

    async def load_data(self, dialog: "Dialog", manager: DialogManager) -> Dict:
        if not self.getter:
            return {}
        return await self.getter(**manager.data)

    async def process_message(self, message: Message, dialog: Dialog, manager: DialogManager):
        if self.on_message:
            await self.on_message.process_message(message, dialog, manager)

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.keyboard:
            await self.keyboard.process_callback(c, dialog, manager)

    async def show(self, dialog: Dialog, manager: DialogManager) -> Message:
        logger.debug("Show window: %s", self)
        current_data = await self.load_data(dialog, manager)
        text = await self.render_text(current_data, manager)
        kbd = await self.render_kbd(current_data, manager)
        event = manager.event
        context = manager.context
        if isinstance(event, CallbackQuery):
            if text == event.message.text:
                if kbd != event.message.reply_markup:
                    return await event.message.edit_reply_markup(reply_markup=kbd)
                else:
                    return event.message
            else:
                return await event.message.edit_text(
                    text=text, reply_markup=kbd, parse_mode=self.parse_mode
                )
        elif isinstance(event, DialogUpdateEvent):
            if context and context.last_message_id:
                try:
                    return await event.bot.edit_message_text(
                        message_id=context.last_message_id, chat_id=event.chat.id,
                        text=text, reply_markup=kbd, parse_mode=self.parse_mode
                    )
                except (MessageNotModified, MessageCantBeEdited):
                    pass  # nothing to update
        else:
            if context and context.last_message_id:
                try:
                    await manager.event.bot.edit_message_reply_markup(
                        message_id=context.last_message_id, chat_id=manager.event.chat.id
                    )
                except (MessageNotModified, MessageCantBeEdited):
                    pass  # nothing to remove
            return await manager.event.bot.send_message(
                chat_id=event.chat.id, text=text, reply_markup=kbd, parse_mode=self.parse_mode
            )

    def get_state(self) -> State:
        return self.state

    def find(self, widget_id) -> Optional[Actionable]:
        if self.keyboard:
            res = self.keyboard.find(widget_id)
            if res:
                return res
        if self.on_message:
            return self.on_message.find(widget_id)
        return None

    def __repr__(self):
        return f"<{self.__class__.__qualname__}({self.state})>"
