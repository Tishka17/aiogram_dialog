import html
import logging
from dataclasses import dataclass
from typing import List, Optional, Any

from aiogram import Bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import User, Chat, Message, ContentType, CallbackQuery
from jinja2 import Environment, PackageLoader, select_autoescape

from aiogram_dialog import DialogRegistry, DialogManager, Dialog
from aiogram_dialog.context.context import Context
from aiogram_dialog.context.events import (
    DialogUpdateEvent, Action, StartMode, Data,
)
from aiogram_dialog.context.stack import Stack
from aiogram_dialog.manager.dialog import ManagedDialogAdapter
from aiogram_dialog.manager.protocols import (
    NewMessage, DialogRegistryProto, MediaAttachment,
    ManagedDialogAdapterProto,
)
from aiogram_dialog.utils import remove_indent_id


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
    text_input: Optional[RenderButton]
    attachment_input: Optional[RenderButton]


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

    async def switch_to(self, state: State) -> None:
        self.set_state(state)

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
    ) -> None:
        self.set_state(state)

    async def done(self, result: Any = None) -> None:
        self.set_state(State("-"))

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
        simulate_events: bool,
) -> RenderButton:
    if not simulate_events:
        return RenderButton(title=title, state=state.state)
    try:
        manager.set_state(state)
        _, callback = remove_indent_id(callback)
        await dialog._callback_handler(
            CallbackQuery(data=callback), dialog_manager=manager,
        )
    except Exception:
        logging.debug("Click %s", callback)
    state = manager.current_context().state
    return RenderButton(title=title, state=state.state)


async def render_input(
        manager: FakeManager,
        state: State, dialog: Dialog,
        content_type: str, simulate_events: bool,
) -> Optional[RenderButton]:
    if not simulate_events:
        return None
    message = Message(message_id=1, **{content_type: "<stub>"})
    try:
        manager.set_state(state)
        await dialog._message_handler(message, dialog_manager=manager)
    except Exception:
        logging.debug("Input %s", content_type)

    if state == manager.current_context().state:
        logging.debug("State not changed")
        return None
    logging.debug("State changed %s >> %s",
                  state, manager.current_context().state)
    return RenderButton(
        title=content_type,
        state=manager.current_context().state.state,
    )


async def create_window(
        state: State, message: NewMessage, manager: FakeManager,
        dialog: Dialog, simulate_events: bool,
) -> RenderWindow:
    if message.parse_mode is None or message.parse_mode == "None":
        text = html.escape(message.text)
    else:
        text = message.text
    keyboard = []
    for row in message.reply_markup.inline_keyboard:
        keyboard_row = []
        for button in row:
            keyboard_row.append(await create_button(
                title=button.text, callback=button.callback_data,
                manager=manager, dialog=dialog, state=state,
                simulate_events=simulate_events,
            ))
        keyboard.append(keyboard_row)

    return RenderWindow(
        message=text.replace("\n", "<br>"),
        state=state.state,
        photo=create_photo(media=message.media),
        keyboard=keyboard,
        text_input=await render_input(
            manager=manager, state=state, dialog=dialog,
            content_type=ContentType.TEXT, simulate_events=simulate_events
        ),
        attachment_input=await render_input(
            manager=manager, state=state, dialog=dialog,
            content_type=ContentType.PHOTO, simulate_events=simulate_events
        ),
    )


async def render_dialog(
        manager: FakeManager, group: StatesGroup,
        dialog: Dialog, simulate_events: bool,
) -> RenderDialog:
    manager.set_dialog(dialog)
    windows = []
    for state in group.states:
        manager.set_state(state)
        await dialog.show(manager)
        windows.append(await create_window(
            manager=manager, state=state, dialog=dialog,
            message=manager.new_message, simulate_events=simulate_events,
        ))

    return RenderDialog(state_group=str(group), windows=windows)


async def render_preview(
        registry: DialogRegistry, file: str,
        simulate_events: bool = False,
):
    fake_manager = FakeManager(registry)
    Bot.set_current(registry.dp.bot)
    dialogs = [
        await render_dialog(
            manager=fake_manager, group=group, dialog=dialog,
            simulate_events=simulate_events,
        )
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
