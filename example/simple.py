import asyncio
import logging
import os.path
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ContentType

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Multi


src_dir = os.path.normpath(os.path.join(__file__, os.path.pardir))

API_TOKEN = "PLACE YOUR TOKEN HERE"


class DialogSG(StatesGroup):
    greeting = State()
    age = State()
    finish = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    age = dialog_manager.current_context().dialog_data.get("age", None)
    return {
        "name": dialog_manager.current_context().dialog_data.get("name", ""),
        "age": age,
        "can_smoke": age in ("18-25", "25-40", "40+"),
    }


async def name_handler(m: Message, dialog: ManagedDialogAdapterProto,
                       manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await m.answer(f"Nice to meet you, {m.text}")
    await dialog.next()


async def on_finish(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("Thank you. To start again click /start")
    await manager.done()


async def on_age_changed(c: ChatEvent, select: Any, manager: DialogManager,
                         item_id: str):
    manager.current_context().dialog_data["age"] = item_id
    await manager.dialog().next()


dialog = Dialog(
    Window(
        Const("Greetings! Please, introduce yourself:"),
        StaticMedia(
            path=os.path.join(src_dir, "python_logo.png"),
            type=ContentType.PHOTO,
        ),
        MessageInput(name_handler),
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


async def start(m: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(DialogSG.greeting, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    dp.register_message_handler(start, text="/start", state="*")
    registry = DialogRegistry(dp)
    registry.register(dialog)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
