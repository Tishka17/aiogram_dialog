import asyncio
import logging
import os.path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import DialogManager, setup_dialogs, StartMode
from bot_dialogs import states
from bot_dialogs.calendar import calendar_dialog
from bot_dialogs.counter import counter_dialog
from bot_dialogs.layouts import layouts_dialog
from bot_dialogs.main import main_dialog
from bot_dialogs.mutltiwidget import multiwidget_dialog
from bot_dialogs.scrolls import scroll_dialog
from bot_dialogs.select import selects_dialog
from bot_dialogs.switch import switch_dialog


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(states.Main.MAIN, mode=StartMode.RESET_STACK)


dialog_router = Router()
dialog_router.include_routers(
    layouts_dialog,
    scroll_dialog,
    main_dialog,
    calendar_dialog,
    selects_dialog,
    counter_dialog,
    multiwidget_dialog,
    switch_dialog,
)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=os.getenv("BOT_TOKEN"))

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.register(start, F.text == "/start")
    dp.include_router(dialog_router)
    setup_dialogs(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
