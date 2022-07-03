import asyncio
import datetime
import logging
import operator

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto

from aiogram_dialog import (
    Dialog, DialogManager, DialogRegistry, Window, StartMode,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Multiselect, Cancel, Start
from aiogram_dialog.widgets.text import Const, Format

API_TOKEN = "PLACE YOUR TOKEN HERE"


class DialogSG(StatesGroup):
    greeting = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    dialog_data = dialog_manager.current_context().dialog_data
    return {
        "stack": dialog_manager.current_stack(),
        "context": dialog_manager.current_context(),
        "now": datetime.datetime.now(),
        "counter": dialog_data.get("counter", 0),
        "last_text": dialog_data.get("last_text", ""),
        "fruits": [
            ("Apple", 1),
            ("Pear", 2),
            ("Orange", 3),
            ("Banana", 4),
        ]
    }


async def name_handler(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    manager.current_context().dialog_data["last_text"] = m.text
    await m.answer(f"Nice to meet you, {m.text}")


async def on_click(c: CallbackQuery, button: Button, manager: DialogManager):
    counter = manager.current_context().dialog_data.get("counter", 0)
    manager.current_context().dialog_data["counter"] = counter + 1


multi = Multiselect(
    Format("✓ {item[0]}"),  # E.g `✓ Apple`
    Format("{item[0]}"),
    id="check",
    item_id_getter=operator.itemgetter(1),
    items="fruits",
)

dialog = Dialog(
    Window(
        Format("Clicked: {counter}\n"),
        Format("Stack: {stack}\n"),
        Format("Context: {context}\n"),
        Format("Last text: {last_text}\n"),
        Format("{now}"),
        Button(Const("Click me!"), id="btn1", on_click=on_click),
        Start(Const("Start new stack"), id="s1",
              mode=StartMode.NEW_STACK, state=DialogSG.greeting),
        multi,
        Cancel(),
        # Inputs work only in default stack
        # or via reply to a message with buttons
        MessageInput(name_handler),
        state=DialogSG.greeting,
        getter=get_data,
    ),
)


async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.greeting, mode=StartMode.NEW_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)
    registry = DialogRegistry(dp)
    # register handler which resets stack and start dialogs on /start command
    dp.message.register(start, Command(commands=('start', )))
    registry.register(dialog)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
