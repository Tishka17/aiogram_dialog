from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token='BOT TOKEN HERE')
dp = Dispatcher(bot, storage=storage)
