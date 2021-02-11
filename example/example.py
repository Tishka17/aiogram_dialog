import asyncio
import logging
from datetime import datetime
from operator import itemgetter

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window
from aiogram_dialog.manager.protocols import BgManagerProto
from aiogram_dialog.widgets.kbd import Button, Group, Next, Back, Cancel, Checkbox, Row, Radio, Multiselect, Select
from aiogram_dialog.widgets.text import Const, Format, Multi, Progress

API_TOKEN = ""


# ------ Groups

class Register(StatesGroup):
    hello = State()
    name = State()


class Sub(StatesGroup):
    text = State()


# ----- Dialog 1

async def get_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": "Tishka17",
        "age": 19,
        "now": datetime.now().time().strftime("%H:%M:%S"),
        "progress": dialog_manager.context.data("progress", 0),
        "progress2": dialog_manager.context.data("progress2", 0),
    }


async def fun(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("It is fun!")
    asyncio.create_task(background(c, manager.bg()))


async def background(c: CallbackQuery, manager: BgManagerProto):
    count = 20
    for i in range(1, count + 1):
        await asyncio.sleep(1)
        await manager.update({
            "progress": i * 100 / count,
            "progress2": min(100, i * 200 / count)
        })


async def input_fun(m: Message, dialog: Dialog, manager: DialogManager):
    print("input_fun")
    await manager.start(Sub.text, m.text)


items = [("One", 1), ("Two", 2), ("Three", 3), ("Four", 4)]
select = Select(
    Format("{item[0]}"),
    "select",
    itemgetter(0),
    items,
)
radio = Radio(
    Format("🔘 {item[0]}"), Format("◯ {item[0]}"),
    "radio",
    itemgetter(0),
    items,
)
multiselect = Multiselect(
    Format("✓ {item[0]}"), Format("{item[0]}"),
    "mselect",
    itemgetter(0),
    items,
)

dialog1 = Dialog(
    Window(
        Multi(
            Const("Hello, {name}!"),
            Format("Hello, {name}!\n", when=lambda data, w, m: data["age"] > 18),
            Format("Now: {now}"),
            Progress("progress", 10),
            Progress("progress2", 10, filled="🟩"),
            sep="\n",
        ),
        Group(
            Group(
                Button(Format("{name}"), "b1"),
                Button(Const("Is it Fun?"), "b2", on_click=fun),
                Checkbox(Const("Yes"), Const("No"), "check"),
                keep_rows=False
            ),
            select,
            radio,
            multiselect,
            Button(Format("{now}"), "b3"),
            Row(Button(Progress("progress", 5), "b3"), Button(Progress("progress2", 5, filled="🟩"), "b4")),
            Next(),
        ),
        getter=get_data,
        state=Register.hello,
        on_message=input_fun,
    ),
    Window(
        Const("Выберите время начала"),
        Group(
            Group(*[
                Button(Const(f"{h % 24:2}:{m:02}"), f"{h}_{m}")
                for h in range(20, 26) for m in range(0, 60, 15)
            ], keep_rows=False, width=4),
            Group(Button(Const("Позже"), "ltr"), Button(Const("Раньше"), "erl"), keep_rows=False),
            Back(Const("Назад")),
        ),
        state=Register.name
    )
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
    await dialog_manager.start(Register.hello, reset_stack=True)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("aiogram_dialog").setLevel(logging.DEBUG)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)
    dp.register_message_handler(start, text="/start", state="*")
    registry.register(dialog1)
    registry.register(dialog2)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
