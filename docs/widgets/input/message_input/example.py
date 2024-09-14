from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType, Message
from aiogram_dialog import (
    Dialog,
    Window,
    DialogManager,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const


class Main(StatesGroup):
    document = State()


async def document_handler(
        message: Message,
        message_input: MessageInput,
        manager: DialogManager,
):
    manager.dialog_data["document"] = message.document
    await message.answer(f"Your document has been verified!")
    await manager.done()


dialog = Dialog(
    Window(
        Const("Submit your document for verification:"),
        MessageInput(document_handler, content_types=[ContentType.DOCUMENT]),
        state=Main.document,
    ),
)
