import html
from dataclasses import dataclass
from typing import List, Optional

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import User, Chat, Message, ContentType, CallbackQuery
from jinja2 import Environment, PackageLoader, select_autoescape

from aiogram_dialog import DialogRegistry, DialogManager, Dialog
from aiogram_dialog.context.context import Context
from aiogram_dialog.context.events import DialogUpdateEvent, Action
from aiogram_dialog.context.stack import Stack
from aiogram_dialog.manager.dialog import ManagedDialogAdapter
from aiogram_dialog.manager.protocols import (
    NewMessage, DialogRegistryProto, MediaAttachment,
    ManagedDialogAdapterProto,
)


@dataclass
class RenderButton:
    state: str
    title: str


@dataclass
class RenderWindow:
    message: str
    state: str
    keyboard: List[List[RenderButton]]
    photo: Optional[str]


@dataclass
class RenderDialog:
    state_group: str
    windows: List[RenderWindow]


class FakeManager(DialogManager):
    def __init__(self, registry: DialogRegistry):
        self.event = DialogUpdateEvent(
            bot=registry.dp.bot,
            from_user=User(),
            chat=Chat(),
            action=Action.UPDATE,
            data={},
            intent_id=None,
            stack_id=None,
        )
        self._registry = registry
        self._context: Optional[Context] = None
        self._dialog = None
        self.data = {
            "dialog_manager": self
        }

    def set_dialog(self, dialog: Dialog):
        self._dialog = dialog
        self.reset_context()

    def set_state(self, state: State):
        self._context.state = state

    def dialog(self) -> ManagedDialogAdapterProto:
        return ManagedDialogAdapter(self._dialog, self)

    def is_preview(self) -> bool:
        return True

    def reset_context(self) -> None:
        self._context = Context(
            _intent_id="0",
            _stack_id="0",
            start_data={},
            widget_data={},
            dialog_data={},
            state=State(),
        )

    def current_stack(self) -> Optional[Stack]:
        return Stack()

    def current_context(self) -> Optional[Context]:
        return self._context

    async def show(self, new_message: NewMessage) -> Message:
        self.new_message = new_message
        return Message()

    @property
    def registry(self) -> DialogRegistryProto:
        return self._registry


def create_photo(media: Optional[MediaAttachment]) -> Optional[str]:
    if not media:
        return
    if media.type != ContentType.PHOTO:
        return
    if media.url:
        return media.url
    if media.path:
        return media.path
    if media.file_id:
        return str(media.file_id)


async def create_button(
        title: str, callback: str, manager: FakeManager,
        state: State, dialog: Dialog,
) -> RenderButton:
    try:
        manager.set_state(state)
        await dialog._callback_handler(
            CallbackQuery(data=callback), dialog_manager=manager,
        )
        state = manager.current_context().state
    except Exception:
        pass
    return RenderButton(title=title, state=state.state)


async def create_window(
        state: State, msg: NewMessage, manager: FakeManager,
        dialog: Dialog,
) -> RenderWindow:
    if msg.parse_mode is None or msg.parse_mode == "None":
        text = html.escape(msg.text)
    else:
        text = msg.text
    keyboard = []
    for row in msg.reply_markup.inline_keyboard:
        keyboard_row = []
        for button in row:
            keyboard_row.append(await create_button(
                title=button.text, callback=button.callback_data,
                manager=manager, dialog=dialog, state=state,
            ))
        keyboard.append(keyboard_row)

    return RenderWindow(
        message=text.replace("\n", "<br>"),
        state=state.state,
        photo=create_photo(media=msg.media),
        keyboard=keyboard
    )


async def render_dialog(manager: FakeManager, group: StatesGroup,
                        dialog: Dialog) -> RenderDialog:
    manager.set_dialog(dialog)
    windows = []
    for state in group.states:
        manager.set_state(state)
        await dialog.show(manager)
        windows.append(await create_window(
            state, manager.new_message, manager, dialog,
        ))

    return RenderDialog(state_group=str(group), windows=windows)


async def render_preview(registry: DialogRegistry, file: str):
    fake_manager = FakeManager(registry)
    dialogs = [
        await render_dialog(fake_manager, group, dialog)
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
