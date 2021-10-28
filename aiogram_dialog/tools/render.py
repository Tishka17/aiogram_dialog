from dataclasses import dataclass
from typing import List, Optional

from aiogram.dispatcher.filters.state import State
from aiogram.types import Message
from jinja2 import Environment, PackageLoader, select_autoescape

from aiogram_dialog import DialogRegistry, Window, DialogManager, Dialog
from aiogram_dialog.context.context import Context


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

    def current_context(self) -> Optional[Context]:
        return Context(
            _intent_id="0",
            _stack_id="0",
            start_data={},
            widget_data={},
            dialog_data={},
            state=State(),
        )


fake_manager = FakeManager()


async def render_window(window: Window) -> RenderWindow:
    msg = await window.render(None, fake_manager, True)
    return RenderWindow(
        message=msg.text.replace("\n","<br>"),
        state=window.state.state,
        keyboard=[
            [
                RenderButton(title=button.text, state=button.callback_data)
                for button in row
            ]
            for row in msg.reply_markup.inline_keyboard
        ]
    )


async def render_dialog(group: str, dialog: Dialog) -> RenderDialog:
    return RenderDialog(
        state_group=group,
        windows=[
            await render_window(window)
            for window in dialog.windows.values()
        ]
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
