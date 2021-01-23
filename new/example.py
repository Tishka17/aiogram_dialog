import asyncio
import logging
from functools import partial
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from dialog.dialog import Dialog
from dialog.kbd import Button, Group, Next, Back
from dialog.text import Const, Format, Multi
from dialog.window import Window

API_TOKEN = ""


async def get_data(dialog: "Dialog", data: Dict):
    return {"name": "Tishka17", "age": 19}


class Register(StatesGroup):
    hello = State()
    name = State()


async def start(m: Message, dialog: Dialog, **kwargs):
    await dialog.start(m.bot, m.chat.id, m.from_user.id, kwargs)


async def fun(c: CallbackQuery, dialog: Dialog, data: Dict):
    await c.message.answer("It is fun!")


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

    )
    name_window = Window(Const("oook"), Back(), state=Register.name)

    dialog = Dialog(hello_window, name_window)

    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)

    dialog.register(dp)
    dp.register_message_handler(partial(start, dialog=dialog), text="/start", state="*")

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
