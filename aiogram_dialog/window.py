from logging import getLogger
from typing import Dict, Optional, Union, Tuple

from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ParseMode

from aiogram_dialog.manager.protocols import DialogManager
from .dialog import Dialog, DialogWindowProto, DataGetter, MessageParams
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
                 parse_mode: Optional[ParseMode] = None):
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

    async def render(self, dialog: Dialog, manager: DialogManager) -> Tuple[Message, MessageParams]:
        logger.debug("Show window: %s", self)
        current_data = await self.load_data(dialog, manager)
        if isinstance(manager.event, CallbackQuery):
            chat = manager.event.message.chat
        else:
            chat = manager.event.chat
        msg = Message(
            chat=chat,
            text=await self.render_text(current_data, manager),
            reply_markup=await self.render_kbd(current_data, manager),
        )
        params = MessageParams(
            self.parse_mode,
            isinstance(manager.event, Message)
        )
        return msg, params

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
