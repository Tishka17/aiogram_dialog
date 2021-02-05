import asyncio
import os
import logging
from operator import itemgetter

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window
from aiogram_dialog.widgets.kbd import Button, Group, Back, Select, SwitchWindow
from aiogram_dialog.widgets.text import Const, Format

API_TOKEN = os.environ["BOT_TOKEN"]


# ------ Groups

class Register(StatesGroup):
    hello = State()
    name = State()


class Sub(StatesGroup):
    text = State()


# ----- Dialog 1

async def get_data(dialog_manager: DialogManager, **kwargs):
    return {"name": "NoName"}


async def empty(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.answer("It does nothing")


async def rm_message(m: Message, dialog: Dialog, manager: DialogManager):
    await m.delete()


async def on_select_change(q: CallbackQuery, text: str, select_obj: Select, manager: DialogManager):
    if text == items[2][0]:
        await q.answer("Ага, фигней страдаешь!")

items = [("Python Developer", 1), ("Java Developer", 2), ("aiogram_dialog Developer", 3)]
select = Select(
    Format("🔘 {item[0]}"), Format("◯ {item[0]}"),
    "select:",
    itemgetter(0),
    items,
    on_state_changed=on_select_change
)

final_win = Window(
    Format("Поздравляю, {name}, Вы записаны на курс, скоро Вам напишут, ожидайте!"),
    Back(),
    getter=get_data,
    state=Register.name
)

choose_course_win = Window(
    Format("Hello, {name}!"),
    Group(
        Button(Const("Choose Your Course"), "b", on_click=empty),
        select,
        SwitchWindow(Const("Next"), "0", final_win),
    ),
    getter=get_data,
    state=Register.hello,
    on_message=rm_message,
)

dialog = Dialog(states_group=Register)
dialog.push_windows(choose_course_win, final_win)


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
    registry.register(dialog)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
