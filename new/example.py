import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from dialog.dialog import Dialog
from dialog.manager.manager import DialogManager
from dialog.manager.registry import DialogRegistry
from dialog.widgets.kbd import Button, Group, Next, Back, Cancel
from dialog.widgets.text import Const, Format, Multi
from dialog.window import Window

API_TOKEN = ""


# ------ Groups

class Register(StatesGroup):
    hello = State()
    name = State()


class Sub(StatesGroup):
    text = State()


# ----- Dialog 1

async def get_data(dialog_manager: DialogManager, **kwargs):
    return {"name": "Tishka17", "age": 19}


async def fun(c: CallbackQuery, dialog: Dialog, manager: DialogManager):
    await c.message.answer("It is fun!")


async def input_fun(m: Message, dialog: Dialog, manager: DialogManager):
    print("input_fun")
    await manager.start(Sub.text, m.text)


dialog1 = Dialog(Window(
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
),
    Window(Const("oook"), Back(), state=Register.name)
)


# ----- Dialog 2

async def get_data2(dialog_manager: DialogManager, **kwargs):
    return {"text": dialog_manager.current_intent().data}


dialog2 = Dialog(
    Window(Format("Your text is: {text}"), Cancel(), state=Sub.text, getter=get_data2)
)


# --------------

async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(Register.hello)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)
    registry.register(dialog1)
    registry.register(dialog2)
    dp.register_message_handler(start, text="/start", state="*")

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
