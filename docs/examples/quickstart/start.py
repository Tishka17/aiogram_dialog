from aiogram.types import Message
from aiogram_dialog import DialogManager

@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    # Important: always set `reset_stack=True` if you don't want to stack dialogs
    await dialog_manager.start(MySG.main, reset_stack=True)
