import asyncio
import datetime
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window
from aiogram_dialog.context.events import StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

API_TOKEN = "PLACE YOUR TOKEN HERE"


class DialogSG(StatesGroup):
    greeting = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    return {
        "stack": dialog_manager.current_stack(),
        "intent": dialog_manager.current_intent(),
        "now": datetime.datetime.now(),
        "counter": dialog_manager.context.data("counter", 0)
    }


async def name_handler(m: Message, dialog: Dialog, manager: DialogManager):
    await m.answer(f"Nice to meet you, {m.text}")


async def on_click(c: CallbackQuery, button: Button, manager: DialogManager):
    counter = manager.context.data("counter", 0)
    manager.context.set_data("counter", counter + 1)


dialog = Dialog(
    Window(
        Format("Clicked: {counter}\n\n{stack}\n\n{intent}\n\n{now}"),
        Button(Const("Click me!"), id="btn1", on_click=on_click),
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
    dp = Dispatcher(bot, storage=storage)
    dp.register_message_handler(start, text="/start", state="*")
    registry = DialogRegistry(dp)
    registry.register(dialog)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
