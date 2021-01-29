import asyncio
import logging
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from dialog.dialog import Dialog
from dialog.manager.manager import DialogManager
from dialog.manager.registry import DialogRegistry
from dialog.widgets.kbd import Button, Group, Next, Back
from dialog.widgets.text import Const, Format, Multi
from dialog.window import Window

API_TOKEN = ""


async def get_data(dialog: "Dialog", data: Dict):
    return {"name": "Tishka17", "age": 19}


class Register(StatesGroup):
    hello = State()
    name = State()


async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(Register.hello)


async def fun(c: CallbackQuery, dialog: Dialog, manager: DialogManager):
    await c.message.answer("It is fun!")


async def input_fun(m: Message, dialog: Dialog, manager: DialogManager):
    print("input_fun")
    await dialog.switch_to(Register.hello, manager)


async def main():
    hello_window = Window(
        Multi(
            Const("Hello, {name}!"),
            Format("Hello, {name}!", when=lambda data: data["age"] > 18),
            sep="\n\n",
        ),
        Group(
            Group(
                Button(Format("{name}"), "b1"),
                Next(),
                Button(Const("Is it Fun?"), "b2", on_click=fun),
                keep_rows=False
            ),
            Button(Const("3. {name}"), "b3"),
            Group(Next(), Next(), Next(), Next(), width=2, keep_rows=False),
        ),
        getter=get_data,
        state=Register.hello,
        on_message=input_fun,
    )
    name_window = Window(Const("oook"), Back(), state=Register.name)

    dialog = Dialog(hello_window, name_window)

    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)
    registry.register(dialog)

    dp.register_message_handler(start, text="/start", state="*")
    dialog.register(dp)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
