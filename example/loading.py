import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Multi, Progress
from aiogram_dialog import Dialog, DialogManager, Window, DialogRegistry, BgManager

API_TOKEN = "PLACE YOUR TOKEN HERE"


# name input dialog

class Bg(StatesGroup):
    progress = State()


async def get_bg_data(dialog_manager: DialogManager, **kwargs):
    return {
        "progress": dialog_manager.context.data("progress", 0)
    }


bg_dialog = Dialog(
    Window(
        Multi(
            Const("Your click is processing, please wait..."),
            Progress("progress", 10),
        ),
        None,
        Bg.progress,
        getter=get_bg_data,
    ),
)


# main dialog
class MainSG(StatesGroup):
    main = State()


async def start_bg(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(Bg.progress)
    asyncio.create_task(background(c, manager.bg()))


async def background(c: CallbackQuery, manager: BgManager):
    count = 10
    for i in range(1, count + 1):
        await asyncio.sleep(1)
        await manager.update({
            "progress": i * 100 / count,
        })
    await asyncio.sleep(1)
    await manager.done()


main_menu = Dialog(
    Window(
        Const("Press button to start processing"),
        Button(Const("Start"), id="start", on_click=start_bg),
        MainSG.main,
    ),
)


async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.main, reset_stack=True)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("aiogram_dialog").setLevel(logging.DEBUG)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)
    registry.register(bg_dialog)
    registry.register(main_menu)
    dp.register_message_handler(start, text="/start", state="*")

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
