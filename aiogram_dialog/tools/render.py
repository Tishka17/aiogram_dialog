from dataclasses import dataclass
from typing import List, Optional

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from jinja2 import Environment, PackageLoader, select_autoescape

from aiogram_dialog import DialogRegistry, DialogManager, Dialog
from aiogram_dialog.context.context import Context
from aiogram_dialog.dialog import DialogWindowProto


@dataclass
class RenderButton:
    state: str
    title: str


@dataclass
class RenderWindow:
    message: str
    state: str
    keyboard: List[List[RenderButton]]


@dataclass
class RenderDialog:
    state_group: str
    windows: List[RenderWindow]


class FakeManager(DialogManager):
    def __init__(self):
        self.event = Message()
        self._dialog = None
        self.data = {
            "dialog_manager": self
        }

    def set_dialog(self, dialog: Dialog):
        self._dialog = dialog

    def dialog(self) -> Dialog:
        return self._dialog

    def is_preview(self) -> bool:
        return True

    def current_context(self) -> Optional[Context]:
        return Context(
            _intent_id="0",
            _stack_id="0",
            start_data={},
            widget_data={},
            dialog_data={},
            state=State(),
        )


async def render_window(
        manager: FakeManager, state: State, window: DialogWindowProto
) -> RenderWindow:
    msg = await window.render(manager.dialog(), manager)
    return RenderWindow(
        message=msg.text.replace("\n", "<br>"),
        state=state.state,
        keyboard=[
            [
                RenderButton(title=button.text, state=button.callback_data)
                for button in row
            ]
            for row in msg.reply_markup.inline_keyboard
        ]
    )


async def render_dialog(group: StatesGroup, dialog: Dialog) -> RenderDialog:
    fake_manager = FakeManager()
    fake_manager.set_dialog(dialog)
    return RenderDialog(
        state_group=str(group),
        windows=[
            await render_window(fake_manager, state, window)
            for state, window in dialog.windows.items()
        ]  # TODO: use dialog.show() instead of hacking `dialog.windows`
    )


async def render(registry: DialogRegistry, file: str):
    dialogs = [
        await render_dialog(group, dialog)
        for group, dialog in registry.dialogs.items()
    ]
    env = Environment(
        loader=PackageLoader("aiogram_dialog.tools"),
        autoescape=select_autoescape()
    )
    template = env.get_template("message.html")
    res = template.render(dialogs=dialogs)
    with open(file, "w") as f:
        f.write(res)
