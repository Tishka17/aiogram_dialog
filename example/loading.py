import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import (
    BaseDialogManager, Dialog, DialogManager, DialogRegistry,
    StartMode, Window,
)
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Multi, Progress

API_TOKEN = os.getenv("BOT_TOKEN")


# name input dialog

class Bg(StatesGroup):
    progress = State()


async def get_bg_data(dialog_manager: DialogManager, **kwargs):
    context = dialog_manager.current_context()
    return {
        "progress": context.dialog_data.get("progress", 0)
    }


bg_dialog = Dialog(
    Window(
        Multi(
            Const("Your click is processing, please wait..."),
            Progress("progress", 10),
        ),
        state=Bg.progress,
        getter=get_bg_data,
    ),
)


# main dialog
class MainSG(StatesGroup):
    main = State()


async def start_bg(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(Bg.progress)
    asyncio.create_task(background(c, manager.bg()))


async def background(c: CallbackQuery, manager: BaseDialogManager):
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
        state=MainSG.main,
    ),
)


async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("aiogram_dialog").setLevel(logging.DEBUG)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    registry = DialogRegistry(dp)
    registry.register(bg_dialog)
    registry.register(main_menu)
    dp.message.register(start, F.text == "/start")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
