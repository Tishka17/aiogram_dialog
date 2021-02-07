from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

storage = MemoryStorage()
bot = Bot(token='BOT TOKEN HERE')
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class MySG(StatesGroup):
    main = State()


dialog = Dialog(
    Window(
        Const("Hello, unknown person"),
        Button(Const("Useless button"), id="nothing"),
        MySG.main,
    )
)
registry.register(dialog)


@dp.message_handler(commands=["/start"])
async def start(m: Message, dialog_manager: DialogManager):
    # Important: always set `reset_stack=True` if you don't want to stack dialogs
    await dialog_manager.start(MySG.main, reset_stack=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
