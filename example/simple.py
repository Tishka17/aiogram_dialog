import asyncio
import logging
import os.path
from typing import Any

from aiogram import Bot, Dispatcher, F
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, ContentType

from aiogram_dialog import (
    Dialog, DialogManager, DialogRegistry,
    ChatEvent, StartMode, Window,
)
from aiogram_dialog.api.exceptions import UnknownIntent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Row, Select, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Multi

src_dir = os.path.normpath(os.path.join(__file__, os.path.pardir))

API_TOKEN = os.getenv("BOT_TOKEN")


class DialogSG(StatesGroup):
    greeting = State()
    age = State()
    finish = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    age = dialog_manager.dialog_data.get("age", None)
    return {
        "name": dialog_manager.dialog_data.get("name", ""),
        "age": age,
        "can_smoke": age in ("18-25", "25-40", "40+"),
    }


async def name_handler(message: Message, message_input: MessageInput,
                       manager: DialogManager):
    if manager.is_preview():
        await manager.next()
        return
    manager.dialog_data["name"] = message.text
    await message.answer(f"Nice to meet you, {message.text}")
    await manager.next()


async def other_type_handler(message: Message, message_input: MessageInput,
                             manager: DialogManager):
    await message.answer("Text is expected")


async def on_finish(callback: CallbackQuery, button: Button,
                    manager: DialogManager):
    if manager.is_preview():
        await manager.done()
        return
    await callback.message.answer("Thank you. To start again click /start")
    await manager.done()


async def on_age_changed(callback: ChatEvent, select: Any,
                         manager: DialogManager,
                         item_id: str):
    manager.dialog_data["age"] = item_id
    await manager.next()


dialog = Dialog(
    Window(
        Const("Greetings! Please, introduce yourself:"),
        StaticMedia(
            path=os.path.join(src_dir, "python_logo.png"),
            type=ContentType.PHOTO,
        ),
        MessageInput(name_handler, content_types=[ContentType.TEXT]),
        MessageInput(other_type_handler),
        state=DialogSG.greeting,
    ),
    Window(
        Format("{name}! How old are you?"),
        Select(
            Format("{item}"),
            items=["0-12", "12-18", "18-25", "25-40", "40+"],
            item_id_getter=lambda x: x,
            id="w_age",
            on_click=on_age_changed,
        ),
        state=DialogSG.age,
        getter=get_data,
        preview_data={"name": "Tishka17"}
    ),
    Window(
        Multi(
            Format("{name}! Thank you for your answers."),
            Const("Hope you are not smoking", when="can_smoke"),
            sep="\n\n",
        ),
        Row(
            Back(),
            SwitchTo(Const("Restart"), id="restart", state=DialogSG.greeting),
            Button(Const("Finish"), on_click=on_finish, id="finish"),
        ),
        getter=get_data,
        state=DialogSG.finish,
    )
)


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(DialogSG.greeting, mode=StartMode.RESET_STACK)


async def error_handler(event, dialog_manager: DialogManager):
    """Example of handling UnknownIntent Error and starting new dialog"""
    if isinstance(event.exception, UnknownIntent):
        await dialog_manager.start(DialogSG.greeting,
                                   mode=StartMode.RESET_STACK)
    else:
        return UNHANDLED


def new_registry():
    registry = DialogRegistry()
    registry.register(dialog)
    return registry


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.register(start, F.text == "/start")
    dp.errors.register(error_handler)
    registry = new_registry()

    registry.setup(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
