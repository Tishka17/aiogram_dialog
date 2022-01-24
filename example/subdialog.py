import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window, DialogRegistry, Data
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.tools import render_transitions, render_preview
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, Back, Cancel, Row, Start, Next
from aiogram_dialog.widgets.text import Const, Format, Multi

API_TOKEN = "PLACE YOUR TOKEN HERE"


# name input dialog

class NameSG(StatesGroup):
    input = State()
    confirm = State()


async def name_handler(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await dialog.next()


async def get_name_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": dialog_manager.current_context().dialog_data.get("name")
    }


async def on_finish(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done({"name": manager.current_context().dialog_data["name"]})


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
        Row(Back(Const("No")), Button(Const("Yes"), id="yes", on_click=on_finish)),
        state=NameSG.confirm,
        getter=get_name_data,
        preview_add_transitions=[Cancel()],  # hint for graph rendering
        preview_data={"name": "John Doe"}  # for preview rendering
    )
)


# main dialog
class MainSG(StatesGroup):
    main = State()


async def process_result(start_data: Data, result: Any, manager: DialogManager):
    if result:
        manager.current_context().dialog_data["name"] = result["name"]


async def get_main_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": dialog_manager.current_context().dialog_data.get("name"),
    }


async def on_reset_name(c: CallbackQuery, button: Button, manager: DialogManager):
    del manager.current_context().dialog_data["name"]


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
        preview_data={"name": "John Doe"}  # for preview rendering
    ),
    on_process_result=process_result,
)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)
    registry = DialogRegistry(dp)
    registry.register_start_handler(MainSG.main)  # resets stack and start dialogs on /start command
    registry.register(name_dialog)
    registry.register(main_menu)
    render_transitions(registry)  # render graph with current transtions
    await render_preview(registry, "preview.html")  # render windows preview

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
