from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token='BOT TOKEN HERE')
dp = Dispatcher(storage=storage)
registry.setup(dp)  # setup aiogram-dialog registry to interact with dispatcher