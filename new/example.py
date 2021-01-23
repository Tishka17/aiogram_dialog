import asyncio
import logging
from functools import partial
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from dialog.dialog import Dialog
from dialog.kbd import Button, Group
from dialog.text import Const, Format, Multi
from dialog.window import Window

API_TOKEN = ""


async def get_data(dialog: "Dialog", data: Dict):
    return {"name": "Tishka17", "age": 19}


class Register(StatesGroup):
    hello = State()
    name = State()


async def start(m: Message, dialog: Dialog, **kwargs):
    state: FSMContext = kwargs["state"]
    await state.set_state(Register.hello.state)
    await dialog.show(m.bot, m.chat.id, kwargs)


async def fun(c: CallbackQuery, dialog: Dialog, data: Dict):
    await c.message.answer("It is fun!")


async def main():
    window = Window(
        Multi(
            Const("Hello, {name}!"),
            Format("Hello, {name}!", when=lambda data: data["age"] > 18),
            sep="\n\n",
        ),
        Group(
            Group(
                Button(Format("{name}"), "b1"),
                Button(Const("Is it Fun?"), "b2", on_click=fun),
                keep_rows=False
            ),
            Button(Const("3. {name}"), "b3"),
        ),
        getter=get_data,
        state=Register.hello,

    )

    dialog = Dialog(window)

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
