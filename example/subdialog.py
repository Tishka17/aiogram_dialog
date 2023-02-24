import asyncio
import logging
import os
from typing import Any

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from aiogram_dialog import (
    Data, Dialog, DialogManager, DialogProtocol, DialogRegistry, Window,
)
from aiogram_dialog.tools import render_transitions, render_preview
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back, Button, Cancel, Group, Next, Row, Start,
)
from aiogram_dialog.widgets.text import Const, Format, Multi

API_TOKEN = os.getenv("BOT_TOKEN")


# name input dialog
class NameSG(StatesGroup):
    input = State()
    confirm = State()


async def name_handler(
        message: Message, dialog: DialogProtocol, manager: DialogManager
):
    manager.dialog_data["name"] = message.text
    await manager.next()


async def get_name_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": dialog_manager.dialog_data.get("name")
    }


async def on_finish(callback: CallbackQuery, button: Button,
                    manager: DialogManager):
    await manager.done({"name": manager.dialog_data["name"]})


name_dialog = Dialog(
    Window(
        Const("What is your name?"),
        Cancel(),
        MessageInput(name_handler),
        state=NameSG.input,
        preview_add_transitions=[Next()],  # hint for graph rendering
    ),
    Window(
        Format("Your name is `{name}`, it is correct?"),
        Row(
            Back(Const("No")),
            Button(Const("Yes"), id="yes", on_click=on_finish),
        ),
        state=NameSG.confirm,
        getter=get_name_data,
        preview_add_transitions=[Cancel()],  # hint for graph rendering
        preview_data={"name": "John Doe"}  # for preview rendering
    )
)


# main dialog
class MainSG(StatesGroup):
    main = State()


async def process_result(start_data: Data, result: Any,
                         manager: DialogManager):
    if result:
        manager.dialog_data["name"] = result["name"]


async def get_main_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": dialog_manager.dialog_data.get("name"),
    }


async def on_reset_name(callback: CallbackQuery, button: Button,
                        manager: DialogManager):
    del manager.dialog_data["name"]


main_menu = Dialog(
    Window(
        Multi(
            Format("Hello, {name}", when="name"),
            Const("Hello, unknown person", when=~F["name"]),
        ),
        Group(
            Start(Const("Enter name"), id="set", state=NameSG.input),
            Button(Const("Reset name"), id="reset",
                   on_click=on_reset_name, when="name")
        ),
        state=MainSG.main,
        getter=get_main_data,
        preview_data={"name": "John Doe"}  # for preview rendering
    ),
    on_process_result=process_result,
)

registry = DialogRegistry()
registry.register(name_dialog)
registry.register(main_menu)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)

    # render graph with current transtions
    render_transitions(registry)
    # render windows preview
    await render_preview(registry, "preview.html")

    # register default handler,
    # which resets stack and start dialogs on /start command
    registry.register_start_handler(state=MainSG.main, router=dp)
    # setup dispatcher to use dialogs
    registry.setup_dp(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
