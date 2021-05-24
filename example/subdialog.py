import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window, DialogRegistry, StartMode, Data
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, Back, Cancel, Row, Start
from aiogram_dialog.widgets.text import Const, Format, Multi

API_TOKEN = "PLACE YOUR TOKEN HERE"


# name input dialog

class NameSG(StatesGroup):
    input = State()
    confirm = State()


async def name_handler(m: Message, dialog: Dialog, manager: DialogManager):
    manager.context.set_data("name", m.text)
    await dialog.next(manager)


async def get_name_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": dialog_manager.context.data("name", None)
    }


async def on_finish(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done({"name": manager.context.data("name")})


name_dialog = Dialog(
    Window(
        Const("What is your name?"),
        Cancel(),
        MessageInput(name_handler),
        state=NameSG.input,
    ),
    Window(
        Format("Your name is `{name}`, it is correct?"),
        Row(Back(Const("No")), Button(Const("Yes"), id="yes", on_click=on_finish)),
        state=NameSG.confirm,
        getter=get_name_data
    )
)


# main dialog
class MainSG(StatesGroup):
    main = State()


async def process_result(start_data: Data, result: Any, manager: DialogManager):
    if result:
        manager.context.set_data("name", result["name"])


async def get_main_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": dialog_manager.context.data("name", None),
    }


async def on_reset_name(c: CallbackQuery, button: Button, manager: DialogManager):
    manager.context.set_data("name", None)


main_menu = Dialog(
    Window(
        Multi(
            Format("Hello, {name}", when="name"),
            Const("Hello, unknown person", when=lambda data, whenable, manager: not data["name"]),
        ),
        Group(
            Start(Const("Enter name"), id="set", state=NameSG.input),
            Button(Const("Reset name"), id="reset", on_click=on_reset_name, when="name")
        ),
        state=MainSG.main,
        getter=get_main_data,
    ),
    on_process_result=process_result,
)


async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    dp.register_message_handler(start, text="/start", state="*")
    registry = DialogRegistry(dp)
    registry.register(name_dialog)
    registry.register(main_menu)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
