from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.tools import render_transitions
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, Back
from aiogram_dialog.widgets.text import Const


class RenderSG(StatesGroup):
    first = State()
    second = State()
    last = State()


async def on_input(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await dialog.next()  # rendering tool cannot detect this call


dialog = Dialog(
    Window(
        Const("1. First"),
        Next(),
        state=RenderSG.first,
    ),
    Window(
        Const("2. Second"),
        Back(),
        MessageInput(on_input),
        state=RenderSG.second,
        preview_add_transitions=[Next()],  # this is a hint for rendering tool
    ),
    Window(
        Const("3. Last"),
        Back(),
        state=RenderSG.last,
    ),
)

render_transitions([dialog])
