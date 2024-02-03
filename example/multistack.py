import asyncio
import datetime
import logging
import operator
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Multiselect, Start
from aiogram_dialog.widgets.text import Const, Format

API_TOKEN = os.getenv("BOT_TOKEN")


class DialogSG(StatesGroup):
    greeting = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    return {
        "stack": dialog_manager.current_stack(),
        "context": dialog_manager.current_context(),
        "now": datetime.datetime.now(),
        "counter": dialog_manager.dialog_data.get("counter", 0),
        "last_text": dialog_manager.dialog_data.get("last_text", ""),
        "fruits": [
            ("Apple", 1),
            ("Pear", 2),
            ("Orange", 3),
            ("Banana", 4),
        ],
    }


async def name_handler(
        message: Message, message_input: MessageInput, manager: DialogManager,
):
    manager.dialog_data["last_text"] = message.text
    await message.answer(f"Nice to meet you, {message.text}")


async def on_click(callback: CallbackQuery, button: Button,
                   manager: DialogManager):
    counter = manager.dialog_data.get("counter", 0)
    manager.dialog_data["counter"] = counter + 1


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


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.greeting, mode=StartMode.NEW_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_router(dialog)

    # register handler which resets stack and start dialogs on /start command
    dp.message.register(start, CommandStart())
    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
