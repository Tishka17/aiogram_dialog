from logging import getLogger
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from aiogram_dialog.api.entities import Data, LaunchMode, NewMessage
from aiogram_dialog.api.exceptions import UnregisteredWindowError
from aiogram_dialog.api.internal import Widget, WindowProtocol
from aiogram_dialog.api.protocols import (
    DialogManager, DialogProtocol,
)
from .utils import add_indent_id, remove_indent_id
from .widgets.data import PreviewAwareGetter
from .widgets.utils import ensure_data_getter, GetterVariant

logger = getLogger(__name__)

ChatEvent = Union[CallbackQuery, Message]
OnDialogEvent = Callable[[Any, DialogManager], Awaitable]
OnResultEvent = Callable[[Data, Any, DialogManager], Awaitable]
W = TypeVar("W", bound=Widget)

_INVALUD_QUERY_ID_MSG = (
    "query is too old and response timeout expired or query id is invalid"
)


class Dialog(DialogProtocol):
    def __init__(
            self,
            *windows: WindowProtocol,
            on_start: Optional[OnDialogEvent] = None,
            on_close: Optional[OnDialogEvent] = None,
            on_process_result: Optional[OnResultEvent] = None,
            launch_mode: LaunchMode = LaunchMode.STANDARD,
            getter: GetterVariant = None,
            preview_data: GetterVariant = None,
    ):
        self._states_group = windows[0].get_state().group
        self._states: List[State] = []
        for w in windows:
            if w.get_state().group != self._states_group:
                raise ValueError(
                    "All windows must be attached to same StatesGroup",
                )
            state = w.get_state()
            if state in self._states:
                raise ValueError(f"Multiple windows with state {state}")
            self._states.append(state)
        self.windows: Dict[State, WindowProtocol] = dict(
            zip(self._states, windows),
        )
        self.on_start = on_start
        self.on_close = on_close
        self.on_process_result = on_process_result
        self._launch_mode = launch_mode
        self.getter = PreviewAwareGetter(
            ensure_data_getter(getter),
            ensure_data_getter(preview_data),
        )

    @property
    def launch_mode(self) -> LaunchMode:
        return self._launch_mode

    def states(self) -> List[State]:
        return self._states

    async def process_start(
            self,
            manager: DialogManager,
            start_data: Any,
            state: Optional[State] = None,
    ) -> None:
        if state is None:
            state = self._states[0]
        logger.debug("Dialog start: %s (%s)", state, self)
        await manager.switch_to(state)
        await self._process_callback(self.on_start, start_data, manager)

    async def _process_callback(
            self, callback: Optional[OnDialogEvent], *args, **kwargs,
    ):
        if callback:
            await callback(*args, **kwargs)

    async def _current_window(
            self, manager: DialogManager,
    ) -> WindowProtocol:
        try:
            return self.windows[manager.current_context().state]
        except KeyError as e:
            raise UnregisteredWindowError(
                f"No window found for `{manager.current_context().state}` "
                f"Current state group is `{self.states_group_name()}`",
            ) from e

    async def load_data(
            self, manager: DialogManager,
    ) -> Dict:
        data = await manager.load_data()
        data.update(await self.getter(**manager.middleware_data))
        return data

    async def render(self, manager: DialogManager) -> NewMessage:
        logger.debug("Dialog render (%s)", self)
        window = await self._current_window(manager)
        new_message = await window.render(self, manager)
        add_indent_id(new_message, manager.current_context().id)
        return new_message

    async def _message_handler(
            self, message: Message, dialog_manager: DialogManager,
    ):
        intent = dialog_manager.current_context()
        window = await self._current_window(dialog_manager)
        await window.process_message(message, self, dialog_manager)
        if dialog_manager.current_context() == intent:  # no new dialog started
            await dialog_manager.show()

    async def _callback_handler(
            self,
            callback: CallbackQuery,
            dialog_manager: DialogManager,
    ):
        intent = dialog_manager.current_context()
        intent_id, callback_data = remove_indent_id(callback.data)
        cleaned_callback = callback.copy(update={"data": callback_data})
        window = await self._current_window(dialog_manager)
        await window.process_callback(cleaned_callback, self, dialog_manager)
        if dialog_manager.current_context() == intent:  # no new dialog started
            await dialog_manager.show()
        if not dialog_manager.is_preview():
            try:
                await callback.answer()
            except TelegramAPIError as e:
                if _INVALUD_QUERY_ID_MSG in e.message:
                    logger.warning("Cannot answer callback: %s", e)
                else:
                    raise

    def register(
            self, router: Router, *args,
            **filters,
    ) -> None:
        router.callback_query.register(
            self._callback_handler, *args, **filters,
        )
        router.message.register(self._message_handler, *args, **filters)

    def states_group(self) -> Type[StatesGroup]:
        return self._states_group

    def states_group_name(self) -> str:
        return self._states_group.__full_group_name__

    async def process_result(
            self,
            start_data: Data,
            result: Any,
            manager: DialogManager,
    ) -> None:
        await self._process_callback(
            self.on_process_result, start_data, result, manager,
        )

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
