from logging import getLogger
from typing import Any, cast

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message, InputRichMessage, RichBlock

from aiogram_dialog import DialogManager, Data, DialogProtocol
from aiogram_dialog.api.entities import NewMessage, EventContext, EVENT_CONTEXT_KEY

from aiogram_dialog.api.internal import WindowProtocol
from aiogram_dialog.api.internal.render import RichWidget, RenderMode, RichContent, RenderingContext
from aiogram_dialog.dialog import OnResultEvent
from aiogram_dialog.widgets.data import PreviewAwareGetter
from aiogram_dialog.widgets.utils import GetterVariant, ensure_data_getter

logger = getLogger(__name__)

class RichWindow(WindowProtocol):

    def __init__(
            self,
            *widgets: RichWidget,
            state: State,
            getter: GetterVariant = None,
            on_process_result: OnResultEvent | None = None,
            render_mode: RenderMode = RenderMode.RICH_HTML,
            protect_content: bool | None = None,
            preview_data: GetterVariant = None,
    ):
        self.widgets = widgets
        self.state = state
        self.on_process_result = on_process_result
        self.protect_content = protect_content
        self.render_mode = render_mode
        self.getter = PreviewAwareGetter(
            ensure_data_getter(getter),
            ensure_data_getter(preview_data),
        )

    async def process_message(self, message: Message, dialog: "DialogProtocol", manager: DialogManager) -> bool:
        await manager.done()
        pass  # TODO

    async def process_callback(self, callback: CallbackQuery, dialog: "DialogProtocol", manager: DialogManager) -> bool:
        await manager.done()
        pass  # TODO

    async def process_result(self, start_data: Data, result: Any, manager: "DialogManager") -> None:
        pass  # TODO

    async def render(
            self,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> NewMessage:
        logger.debug("Show window: %s", self)
        chat = manager.middleware_data["event_chat"]

        try:
            event_context = cast(
                EventContext, manager.middleware_data.get(EVENT_CONTEXT_KEY),
            )
            rich_content = await self.render_rich(await dialog.load_data(manager), manager, self.render_mode)
            return NewMessage(
                chat=chat,
                thread_id=event_context.thread_id,
                business_connection_id=event_context.business_connection_id,
                protect_content=self.protect_content,
                rich_message=rich_input(rich_content, self.render_mode),
            )
        except Exception:
            logger.error("Cannot render window for state %s", self.state)
            raise

    async def render_rich(self, data: dict[str, Any], context: RenderingContext, mode: RenderMode) -> RichContent:
        try:
            data |= await self.getter(**context.middleware_data)
        except Exception:
            logger.error("Cannot get window data for state %s", self.state)
            raise

        content = RichContent()
        for widget in self.widgets:
            content += await widget.render_rich(data, context, mode)
        return content

    def get_state(self) -> State:
        return self.state

    def find(self, widget_id) -> Any:
        pass


def rich_input(content: RichContent, mode: RenderMode) -> InputRichMessage:
    return InputRichMessage(
        html=content.plain if mode == RenderMode.RICH_HTML else None,
        md=content.plain if mode == RenderMode.RICH_MD else None,
        blocks=content.blocks if mode == RenderMode.RICH_BLOCKS else None,
        media=content.media,
    )