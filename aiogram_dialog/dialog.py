from logging import getLogger
from typing import Dict, Callable, Awaitable, List, Union, Any, Optional, Type, TypeVar
from typing import Protocol

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ContentTypes
from aiogram.utils.exceptions import InvalidQueryID

from .context.events import Data
from .exceptions import UnregisteredWindowError
from .manager.protocols import (
    DialogRegistryProto, ManagedDialogProto, DialogManager, NewMessage,
    LaunchMode,
)
from .utils import add_indent_id, get_media_id
from .widgets.action import Actionable
from .widgets.data import PreviewAwareGetter
from .widgets.utils import (
    ensure_data_getter, GetterVariant,
)

logger = getLogger(__name__)
DIALOG_CONTEXT = "DIALOG_CONTEXT"

ChatEvent = Union[CallbackQuery, Message]
OnDialogEvent = Callable[[Any, DialogManager], Awaitable]
OnResultEvent = Callable[[Data, Any, DialogManager], Awaitable]
W = TypeVar("W", bound=Actionable)


class DialogWindowProto(Protocol):
    async def render_text(self, data: Dict, manager: DialogManager) -> str:
        raise NotImplementedError

    async def render_kbd(self, data: Dict, manager: DialogManager) -> InlineKeyboardMarkup:
        raise NotImplementedError

    async def load_data(self, dialog: "Dialog", manager: DialogManager) -> Dict:
        raise NotImplementedError

    async def process_message(self, m: Message, dialog: "Dialog", manager: DialogManager):
        raise NotImplementedError

    async def process_callback(self, c: CallbackQuery, dialog: "Dialog", manager: DialogManager):
        raise NotImplementedError

    async def render(self, dialog: "Dialog", manager: DialogManager) -> NewMessage:
        raise NotImplementedError

    def get_state(self) -> State:
        raise NotImplementedError

    def find(self, widget_id) -> Optional[Actionable]:
        raise NotImplementedError


class Dialog(ManagedDialogProto):
    def __init__(
            self,
            *windows: DialogWindowProto,
            on_start: Optional[OnDialogEvent] = None,
            on_close: Optional[OnDialogEvent] = None,
            on_process_result: Optional[OnResultEvent] = None,
            launch_mode: LaunchMode = LaunchMode.STANDARD,
            getter: GetterVariant = None,
            preview_data: GetterVariant = None,
    ):
        self._states_group = windows[0].get_state().group
        self.states: List[State] = []
        for w in windows:
            if w.get_state().group != self._states_group:
                raise ValueError("All windows must be attached to same StatesGroup")
            state = w.get_state()
            if state in self.states:
                raise ValueError(f"Multiple windows with state {state}")
            self.states.append(state)
        self.windows: Dict[State, DialogWindowProto] = dict(zip(self.states, windows))
        self.on_start = on_start
        self.on_close = on_close
        self.on_process_result = on_process_result
        self.launch_mode = launch_mode
        self.getter = PreviewAwareGetter(
            ensure_data_getter(getter),
            ensure_data_getter(preview_data),
        )

    async def next(self, manager: DialogManager):
        if not manager.current_context():
            raise ValueError("No intent")
        new_state = self.states[self.states.index(manager.current_context().state) + 1]
        await self.switch_to(new_state, manager)

    async def back(self, manager: DialogManager):
        if not manager.current_context():
            raise ValueError("No intent")
        new_state = self.states[self.states.index(manager.current_context().state) - 1]
        await self.switch_to(new_state, manager)

    async def process_start(self, manager: DialogManager, start_data: Any,
                            state: Optional[State] = None) -> None:
        if state is None:
            state = self.states[0]
        logger.debug("Dialog start: %s (%s)", state, self)
        await self.switch_to(state, manager)
        await self._process_callback(self.on_start, start_data, manager)

    async def _process_callback(self, callback: Optional[OnDialogEvent], *args, **kwargs):
        if callback:
            await callback(*args, **kwargs)

    async def switch_to(self, state: State, manager: DialogManager):
        if state.group != self.states_group():
            raise ValueError(
                f"Cannot switch from `{self.states_group_name()}` "
                f"to another states group {state.group}"
            )
        await manager.switch_to(state)

    async def _current_window(self, manager: DialogManager) -> DialogWindowProto:
        try:
            return self.windows[manager.current_context().state]
        except ValueError as e:
            raise UnregisteredWindowError(
                f"No window found for `{manager.current_context().state}` "
                f"Current state group is `{self.states_group_name()}`"
            ) from e

    async def load_data(self, manager: DialogManager) -> Dict:
        data = await manager.load_data()
        data.update(await self.getter(**manager.data))
        return data

    async def show(self, manager: DialogManager) -> None:
        logger.debug("Dialog show (%s)", self)
        window = await self._current_window(manager)
        new_message = await window.render(self, manager)
        add_indent_id(new_message, manager.current_context().id)
        media_id_storage = manager.registry.media_id_storage
        if new_message.media and not new_message.media.file_id:
            new_message.media.file_id = await media_id_storage.get_media_id(
                path=new_message.media.path,
                url=new_message.media.url,
                type=new_message.media.type,
            )
        stack = manager.current_stack()
        message = await manager.show(new_message)
        stack.last_message_id = message.message_id
        media_id = get_media_id(message)
        if media_id:
            stack.last_media_id = media_id.file_id
            stack.last_media_unique_id = media_id.file_unique_id
        else:
            stack.last_media_id = None
            stack.last_media_unique_id = None

        if new_message.media:
            await media_id_storage.save_media_id(
                path=new_message.media.path,
                url=new_message.media.url,
                type=new_message.media.type,
                media_id=get_media_id(message),
            )

    async def _message_handler(self, m: Message, dialog_manager: DialogManager):
        intent = dialog_manager.current_context()
        window = await self._current_window(dialog_manager)
        await window.process_message(m, self, dialog_manager)
        if dialog_manager.current_context() == intent:  # no new dialog started
            await self.show(dialog_manager)

    async def _callback_handler(self, c: CallbackQuery, dialog_manager: DialogManager):
        intent = dialog_manager.current_context()
        window = await self._current_window(dialog_manager)
        await window.process_callback(c, self, dialog_manager)
        if dialog_manager.current_context() == intent:  # no new dialog started
            await self.show(dialog_manager)
        if not dialog_manager.is_preview():
            try:
                await c.answer()
            except InvalidQueryID as e:
                logger.warning("Cannot answer callback: %s", e)

    async def _update_handler(self, event: ChatEvent, dialog_manager: DialogManager):
        await self.show(dialog_manager)

    def register(self, registry: DialogRegistryProto, dp: Dispatcher, *args, **filters) -> None:
        if "state" not in filters:
            filters["state"] = "*"
        dp.register_callback_query_handler(self._callback_handler, *args, **filters)
        if "content_types" not in filters:
            filters["content_types"] = ContentTypes.ANY
        dp.register_message_handler(self._message_handler, *args, **filters)

    def states_group(self) -> Type[StatesGroup]:
        return self._states_group

    def states_group_name(self) -> str:
        return self._states_group.__full_group_name__

    async def process_result(self, start_data: Data, result: Any, manager: DialogManager):
        await self._process_callback(self.on_process_result, start_data, result, manager)

    async def process_close(self, result: Any, manager: DialogManager):
        await self._process_callback(self.on_close, result, manager)

    def find(self, widget_id) -> Optional[W]:
        for w in self.windows.values():
            widget = w.find(widget_id)
            if widget:
                return widget
        return None

    def __repr__(self):
        return f"<{self.__class__.__qualname__}({self.states_group()})>"
