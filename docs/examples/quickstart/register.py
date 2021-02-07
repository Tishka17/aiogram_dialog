from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import Window, Dialog, DialogRegistry
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

storage = MemoryStorage()
bot = Bot(token='BOT TOKEN HERE')
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)  # this is required to use `aiogram_dialog`


class MySG(StatesGroup):
    main = State()


dialog = Dialog(
    Window(
        Const("Hello, unknown person"),
        Button(Const("Useless button"), id="nothing"),
        MySG.main,
    )
)
registry.register(dialog)  # register a dialog

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
