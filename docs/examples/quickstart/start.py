from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

@dp.message(commands=["start"])
async def start(message: Message, dialog_manager: DialogManager):
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)
