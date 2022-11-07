import html
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Chat, ContentType, Message, User
from jinja2 import Environment, PackageLoader, select_autoescape

from aiogram_dialog import (
    Dialog, DialogManager, DialogProtocol, DialogRegistry,
)
from aiogram_dialog.api.entities import (
    ChatEvent,
    Context,
    Data,
    DialogAction,
    DialogUpdateEvent,
    MediaAttachment,
    NewMessage,
    ShowMode,
    Stack,
    StartMode,
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
    text_input: Optional[RenderButton]
    attachment_input: Optional[RenderButton]


@dataclass
class RenderDialog:
    state_group: str
    windows: List[RenderWindow]


class FakeManager(DialogManager):
    def __init__(self, registry: DialogRegistry):
        self._event = DialogUpdateEvent(
            from_user=User(id=1, is_bot=False, first_name="Fake"),
            chat=Chat(id=1, type="private"),
            action=DialogAction.UPDATE,
            data={},
            intent_id=None,
            stack_id=None,
        )
        self._registry = registry
        self._context: Optional[Context] = None
        self._dialog: Optional[DialogProtocol] = None
        self._data = {
            "dialog_manager": self,
            "event_chat": Chat(id=1, type="private"),
            "event_from_user": User(id=1, is_bot=False, first_name="Fake"),
        }

    @property
    def data(self) -> Dict:
        return self._data

    @property
    def event(self) -> ChatEvent:
        return self._event

    async def load_data(self) -> Dict:
        return {}

    async def close_manager(self) -> None:
        pass

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        self.reset_context()

    def set_dialog(self, dialog: Dialog):
        self._dialog = dialog
        self.reset_context()

    def set_state(self, state: State):
        self._context.state = state

    def is_preview(self) -> bool:
        return True

    @property
    def middleware_data(self) -> Dict:
        return {
            "event_chat": self.event.chat,
            "dialog_manager": self,
        }

    @property
    def dialog_data(self) -> Dict:
        return self._context.dialog_data

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
            show_mode: ShowMode = ShowMode.AUTO,
    ) -> None:
        self.set_state(state)

    async def done(self, result: Any = None) -> None:
        self.set_state(State("-"))

    def current_stack(self) -> Optional[Stack]:
        return Stack()

    def current_context(self) -> Optional[Context]:
        return self._context

    async def show_raw(self) -> NewMessage:
        return await self._dialog.render(self)


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
        title: str,
        callback: str,
        manager: FakeManager,
        state: State,
        dialog: Dialog,
        simulate_events: bool,
) -> RenderButton:
    if not simulate_events:
        return RenderButton(title=title, state=state.state)
    callback_query = CallbackQuery(
        id="1",
        from_user=User(id=1, is_bot=False, first_name=""),
        chat_instance="",
        data=callback,
    )
    manager.set_state(state)
    try:
        await dialog._callback_handler(callback_query, dialog_manager=manager)
    except Exception:  # noqa: B902
        logging.debug("Click %s", callback)
    state = manager.current_context().state
    return RenderButton(title=title, state=state.state)


async def render_input(
        manager: FakeManager,
        state: State,
        dialog: Dialog,
        content_type: str,
        simulate_events: bool,
) -> Optional[RenderButton]:
    if not simulate_events:
        return None
    if content_type == ContentType.PHOTO:
        data = {content_type: []}
    else:
        data = {content_type: "<stub>"}
    message = Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=1, type="private"),
        **data,
    )
    manager.set_state(state)
    try:
        await dialog._message_handler(message, dialog_manager=manager)
    except Exception:  # noqa: B902
        logging.debug("Input %s", content_type)

    if state == manager.current_context().state:
        logging.debug("State not changed")
        return None
    logging.debug(
        "State changed %s >> %s", state, manager.current_context().state,
    )
    return RenderButton(
        title=content_type,
        state=manager.current_context().state.state,
    )


async def create_window(
        state: State,
        message: NewMessage,
        manager: FakeManager,
        dialog: Dialog,
        simulate_events: bool,
) -> RenderWindow:
    if message.parse_mode is None or message.parse_mode == "None":
        text = html.escape(message.text)
    else:
        text = message.text
    keyboard = []
    for row in message.reply_markup.inline_keyboard:
        keyboard_row = []
        for button in row:
            keyboard_row.append(
                await create_button(
                    title=button.text,
                    callback=button.callback_data,
                    manager=manager,
                    dialog=dialog,
                    state=state,
                    simulate_events=simulate_events,
                ),
            )
        keyboard.append(keyboard_row)

    return RenderWindow(
        message=text.replace("\n", "<br>"),
        state=state.state,
        photo=create_photo(media=message.media),
        keyboard=keyboard,
        text_input=await render_input(
            manager=manager,
            state=state,
            dialog=dialog,
            content_type=ContentType.TEXT,
            simulate_events=simulate_events,
        ),
        attachment_input=await render_input(
            manager=manager,
            state=state,
            dialog=dialog,
            content_type=ContentType.PHOTO,
            simulate_events=simulate_events,
        ),
    )


async def render_dialog(
        manager: FakeManager,
        group: StatesGroup,
        dialog: Dialog,
        simulate_events: bool,
) -> RenderDialog:
    manager.set_dialog(dialog)
    windows = []
    for state in group.__states__:
        manager.set_state(state)
        new_message = await manager.show_raw()
        windows.append(
            await create_window(
                manager=manager,
                state=state,
                dialog=dialog,
                message=new_message,
                simulate_events=simulate_events,
            ),
        )

    return RenderDialog(state_group=str(group), windows=windows)


async def render_preview(
        registry: DialogRegistry,
        file: str,
        simulate_events: bool = False,
):
    fake_manager = FakeManager(registry)
    dialogs = [
        await render_dialog(
            manager=fake_manager,
            group=group,
            dialog=dialog,
            simulate_events=simulate_events,
        )
        for group, dialog in registry.dialogs.items()
    ]
    env = Environment(
        loader=PackageLoader("aiogram_dialog.tools"),
        autoescape=select_autoescape(),
    )
    template = env.get_template("message.html")
    res = template.render(dialogs=dialogs)
    with open(file, "w", encoding="utf-8") as f:
        f.write(res)
