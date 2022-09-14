import dataclasses
from typing import Any, Dict, Optional

from aiogram.fsm.state import State
from aiogram.types import Message

from aiogram_dialog.api.entities import (
    ChatEvent, Data, ShowMode, StartMode,
)
from aiogram_dialog.api.entities import Context, Stack
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.api.protocols import BaseDialogManager, DialogManager


class SubManager(DialogManager):
    def __init__(
            self,
            widget: Widget,
            manager: DialogManager,
            widget_id: str,
            item_id: str,
    ):
        self.widget = widget
        self.manager = manager
        self.widget_id = widget_id
        self.item_id = item_id

    @property
    def event(self) -> ChatEvent:
        return self.manager.event

    @property
    def middleware_data(self) -> Dict:
        """Middleware data."""
        return self.manager.middleware_data

    @property
    def dialog_data(self) -> Dict:
        """Dialog data for current context."""
        return self.current_context().dialog_data

    @property
    def start_data(self) -> Dict:
        """Start data for current context."""
        return self.manager.start_data

    def current_context(self) -> Optional[Context]:
        context = self.manager.current_context()
        data = context.widget_data.setdefault(self.widget_id, {})
        row_data = data.setdefault(self.item_id, {})
        return dataclasses.replace(context, widget_data=row_data)

    def is_preview(self) -> bool:
        return self.manager.is_preview()

    def current_stack(self) -> Optional[Stack]:
        return self.manager.current_stack()

    async def close_manager(self) -> None:
        return await self.manager.close_manager()

    async def show(self) -> Message:
        return await self.manager.show()

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        return await self.manager.reset_stack(remove_keyboard)

    async def load_data(self) -> Dict:
        return await self.manager.load_data()

    def find(self, widget_id) -> Optional[Any]:
        widget = self.widget.find(widget_id)
        if not widget:
            return None
        return widget.managed(self)

    def find_in_parent(self, widget_id) -> Optional[Any]:
        return self.manager.find(widget_id)

    @property
    def show_mode(self) -> ShowMode:
        return self.manager.show_mode

    @show_mode.setter
    def show_mode(self, show_mode: ShowMode) -> None:
        self.manager.show_mode = show_mode

    async def next(self) -> None:
        await self.manager.next()

    async def back(self) -> None:
        await self.manager.back()

    async def done(self, result: Any = None) -> None:
        await self.manager.done(result=result)

    async def mark_closed(self) -> None:
        await self.manager.mark_closed()

    async def start(self, state: State, data: Data = None,
                    mode: StartMode = StartMode.NORMAL,
                    show_mode: ShowMode = ShowMode.AUTO) -> None:
        await self.manager.start(
            state=state, data=data, mode=mode, show_mode=show_mode,
        )

    async def switch_to(self, state: State) -> None:
        await self.manager.switch_to(state)

    async def update(self, data: Dict) -> None:
        self.current_context().dialog_data.update(data)
        await self.show()

    def bg(self, user_id: Optional[int] = None, chat_id: Optional[int] = None,
           stack_id: Optional[str] = None,
           load: bool = False) -> BaseDialogManager:
        return self.manager.bg(
            user_id=user_id, chat_id=chat_id, stack_id=stack_id, load=load,
        )
