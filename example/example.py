import asyncio
import logging
from datetime import datetime
from operator import itemgetter

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window
from aiogram_dialog.widgets.kbd import Button, Group, Next, Back, Cancel, Checkbox, Select
from aiogram_dialog.widgets.text import Const, Format, Multi

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


async def fun(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("It is fun!")


async def input_fun(m: Message, dialog: Dialog, manager: DialogManager):
    print("input_fun")
    await manager.start(Sub.text, m.text)


items = [("One", 1), ("Two", 2), ("Three", 3), ("Four", 4)]
select = Select(
    Format("🔘 {item[0]}"), Format("◯ {item[0]}"),
    "select:",
    itemgetter(0),
    items,
    "select1"
)
multiselect = Select(
    Format("✓ {item[0]}"), Format("{item[0]}"),
    "mselect:",
    itemgetter(0),
    items,
    "mselect",
    multiple=True
)

dialog1 = Dialog(Window(
    Multi(
        Const("Hello, {name}!"),
        Format("Hello, {name}!", when=lambda data, w, m: data["age"] > 18),
        sep="\n\n",
    ),
    Group(
        Group(
            Button(Format("{name}"), "b1"),
            Button(Const("Is it Fun?"), "b2", on_click=fun),
            Checkbox(Const("Yes"), Const("No"), "check", "check"),
            keep_rows=False
        ),
        select,
        multiselect,
        Button(Const("3. {name}"), "b3"),
        Next(),
    ),
    getter=get_data,
    state=Register.hello,
    on_message=input_fun,
),
    Window(Const("Выберите время начала"),
           Group(
               Group(*[
                   Button(Const(f"{h % 24:2}:{m:02}"), f"{h}:{m}")
                   for h in range(20, 26) for m in range(0, 60, 15)
               ], keep_rows=False, width=4),
               Group(Button(Const("Позже"), "ltr"), Button(Const("Раньше"), "erl"), keep_rows=False),
               Back(Const("Назад")),
           ), state=Register.name)
)


# ----- Dialog 2

async def get_data2(dialog_manager: DialogManager, **kwargs):
    return {
        "text": dialog_manager.current_intent().data,
        "now": datetime.now().isoformat(),
    }


dialog2 = Dialog(
    Window(
        Format("Your text is: {text}\nCurrent time: {now}"),
        Cancel(), state=Sub.text, getter=get_data2,
        on_message=input_fun
    )
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
