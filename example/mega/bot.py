import asyncio
import logging
import os.path

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import DialogManager, DialogRegistry, StartMode
from bot_dialogs import states
from bot_dialogs.calendar import calendar_dialog
from bot_dialogs.layouts import layouts_dialog
from bot_dialogs.main import main_dialog
from bot_dialogs.scrolls import scroll_dialog


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(states.Main.MAIN, mode=StartMode.RESET_STACK)


def get_registry():
    registry = DialogRegistry()
    registry.register(layouts_dialog)
    registry.register(scroll_dialog)
    registry.register(main_dialog)
    registry.register(calendar_dialog)
    return registry


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=os.getenv("BOT_TOKEN"))

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.register(start, F.text == "/start")

    registry = get_registry()
    registry.setup_dp(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
